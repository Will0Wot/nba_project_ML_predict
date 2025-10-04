"""Command line interface for training and using the NBA matchup engine."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from . import data as data_utils
from .model import MatchupPredictor


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("csv/player_game_logs_2022.csv"),
        help="Path to the CSV file containing player game logs.",
    )
    parser.add_argument(
        "--team",
        type=str,
        help="Team abbreviation for which to generate a probability estimate.",
    )
    parser.add_argument(
        "--opponent",
        type=str,
        help="Opponent team abbreviation.",
    )
    parser.add_argument(
        "--home",
        action="store_true",
        help="Flag indicating the specified team is playing at home.",
    )
    parser.add_argument(
        "--weight-by-minutes",
        action="store_true",
        help="Use minute-weighted averages when constructing season vectors.",
    )
    parser.add_argument(
        "--test-split",
        type=float,
        default=0.2,
        help="Fraction of games to reserve for evaluation (chronological split).",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=5,
        help="Number of features to display in the explanation output.",
    )
    return parser.parse_args()


def chronological_split(df: pd.DataFrame, test_size: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = df.sort_values("GAME_DATE").reset_index(drop=True)
    split_index = int(len(df) * (1 - test_size))
    return df.iloc[:split_index], df.iloc[split_index:]


def main() -> None:
    args = parse_arguments()

    player_logs = data_utils.load_player_logs(args.data)
    team_games = data_utils.prepare_team_game_features(player_logs)
    matchup_df, diff_feature_columns = data_utils.build_matchup_dataset(team_games)

    train_df, test_df = chronological_split(matchup_df, args.test_split)

    predictor = MatchupPredictor()
    predictor.fit(train_df, feature_columns=(*diff_feature_columns, "HOME"))
    evaluation = predictor.evaluate(test_df)

    print("Evaluation metrics:")
    for key, value in evaluation.as_dict().items():
        print(f"  {key:>10}: {value:.3f}")

    if args.team and args.opponent:
        try:
            season_averages = data_utils.compute_team_season_averages(
                team_games, weight_by_minutes=args.weight_by_minutes
            )
            prediction_frame = data_utils.build_season_matchup_frame(
                season_averages=season_averages,
                diff_feature_columns=diff_feature_columns,
                team=args.team.upper(),
                opponent=args.opponent.upper(),
                home=args.home,
            )
            fallback_teams = set(
                prediction_frame.attrs.get("fallback_teams", set())
            )
        except ValueError as exc:
            print(f"\nUnable to generate prediction: {exc}")
            return

        probability = predictor.predict_proba(prediction_frame)[0]
        explanation = predictor.explain(
            prediction_frame, top_n=args.top_n
        )[0]

        print("\nPrediction summary:")
        print(
            f"  {args.team.upper()} vs {args.opponent.upper()}"
            f" ({'home' if args.home else 'away'})"
        )
        print(f"  Win probability: {probability:.2%}")
        print("  Key feature contributions:")
        for feature, contribution in explanation.items():
            if feature == "probability":
                continue
            print(f"    {feature:>20}: {contribution:+.3f}")

        if fallback_teams:
            teams = ", ".join(sorted(fallback_teams))
            print(
                "\nNote: season averages were unavailable for"
                f" {teams}. Used league-average fallback statistics instead."
            )


if __name__ == "__main__":
    main()
