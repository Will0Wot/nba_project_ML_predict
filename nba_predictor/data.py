"""Data loading and feature engineering utilities for NBA matchup prediction.

This module provides helper functions to transform raw player game logs into
team-level matchup features suitable for machine learning models.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence, Tuple

import pandas as pd


# Raw player log column names as returned by the nba_api stats endpoints.
PLAYER_LOG_COLUMNS: Sequence[str] = [
    "SEASON_ID",
    "PLAYER_ID",
    "GAME_ID",
    "GAME_DATE",
    "MATCHUP",
    "WL",
    "MIN",
    "FGM",
    "FGA",
    "FG_PCT",
    "FG3M",
    "FG3A",
    "FG3_PCT",
    "FTM",
    "FTA",
    "FT_PCT",
    "OREB",
    "DREB",
    "REB",
    "AST",
    "STL",
    "BLK",
    "TOV",
    "PF",
    "PTS",
    "PLUS_MINUS",
    "VIDEO_AVAILABLE",
    "PLAYER_NAME",
]

# Statistics that should be summed when aggregating from player to team level.
TEAM_SUM_COLUMNS: Sequence[str] = [
    "MIN",
    "FGM",
    "FGA",
    "FG3M",
    "FG3A",
    "FTM",
    "FTA",
    "OREB",
    "DREB",
    "REB",
    "AST",
    "STL",
    "BLK",
    "TOV",
    "PF",
    "PTS",
    "PLUS_MINUS",
]

# Statistics that represent rates/percentages and should be averaged.
TEAM_MEAN_COLUMNS: Sequence[str] = ["FG_PCT", "FG3_PCT", "FT_PCT"]


@dataclass(frozen=True)
class TeamGameFeatures:
    """Container holding engineered team game features and their metadata."""

    data: pd.DataFrame
    feature_columns: Tuple[str, ...]


def _parse_team(matchup: str) -> str:
    return matchup.split(" ")[0]


def _parse_opponent(matchup: str) -> str:
    if "vs." in matchup:
        return matchup.split("vs. ")[-1]
    if "@" in matchup:
        return matchup.split("@ ")[-1]
    raise ValueError(f"Unrecognised matchup format: {matchup!r}")


def load_player_logs(csv_path: Path | str) -> pd.DataFrame:
    """Load raw player game logs from a CSV file.

    Parameters
    ----------
    csv_path:
        Path to the CSV export containing player game logs.

    Returns
    -------
    pandas.DataFrame
        A dataframe with well named columns and useful helper flags such as
        ``TEAM_ABBREVIATION``, ``OPPONENT_ABBREVIATION`` and ``HOME``.
    """

    df = pd.read_csv(csv_path, header=None, names=PLAYER_LOG_COLUMNS)

    df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])

    for column in TEAM_SUM_COLUMNS + list(TEAM_MEAN_COLUMNS) + ["PLUS_MINUS"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["TEAM_ABBREVIATION"] = df["MATCHUP"].apply(_parse_team)
    df["OPPONENT_ABBREVIATION"] = df["MATCHUP"].apply(_parse_opponent)
    df["HOME"] = df["MATCHUP"].str.contains("vs.")
    df["WIN"] = (df["WL"] == "W").astype(int)

    return df


def prepare_team_game_features(player_logs: pd.DataFrame) -> TeamGameFeatures:
    """Aggregate player logs into per-team game features.

    The function consolidates player level statistics into a single row per
    team per game, summing counting stats and averaging shooting percentages.
    A player count field is added to provide additional context about rotation
    depth during the matchup.
    """

    aggregation = {
        **{column: "sum" for column in TEAM_SUM_COLUMNS},
        **{column: "mean" for column in TEAM_MEAN_COLUMNS},
        "PLAYER_NAME": "count",
        "GAME_DATE": "first",
    }

    group_columns = [
        "GAME_ID",
        "TEAM_ABBREVIATION",
        "OPPONENT_ABBREVIATION",
        "HOME",
        "WIN",
    ]

    team_games = (
        player_logs.groupby(group_columns, as_index=False).agg(aggregation)
    )

    team_games = team_games.rename(columns={"PLAYER_NAME": "PLAYER_COUNT"})
    feature_columns = tuple(
        column
        for column in team_games.columns
        if column
        not in {
            "GAME_ID",
            "TEAM_ABBREVIATION",
            "OPPONENT_ABBREVIATION",
            "HOME",
            "WIN",
            "GAME_DATE",
        }
    )

    # Ensure deterministic column order: metadata first, then features.
    ordered_columns = [
        "GAME_ID",
        "GAME_DATE",
        "TEAM_ABBREVIATION",
        "OPPONENT_ABBREVIATION",
        "HOME",
        "WIN",
        *feature_columns,
    ]
    team_games = team_games[ordered_columns]

    return TeamGameFeatures(data=team_games, feature_columns=feature_columns)


def build_matchup_dataset(team_games: TeamGameFeatures) -> Tuple[pd.DataFrame, Tuple[str, ...]]:
    """Construct a matchup-level modelling dataset.

    Parameters
    ----------
    team_games:
        Output from :func:`prepare_team_game_features`.

    Returns
    -------
    tuple
        A tuple containing the enriched modelling dataframe and the ordered
        feature names corresponding to the ``*_DIFF`` columns that can be used
        for training.
    """

    df = team_games.data
    feature_columns = team_games.feature_columns

    opponent_df = df.rename(
        columns={
            "TEAM_ABBREVIATION": "OPPONENT_ABBREVIATION",
            "OPPONENT_ABBREVIATION": "TEAM_ABBREVIATION",
            "HOME": "OPPONENT_HOME",
            "WIN": "OPPONENT_WIN",
        }
    )

    merged = df.merge(
        opponent_df,
        on=["GAME_ID", "TEAM_ABBREVIATION", "OPPONENT_ABBREVIATION"],
        suffixes=("", "_OPP"),
    )

    diff_feature_columns: List[str] = []
    for column in feature_columns:
        diff_column = f"{column}_DIFF"
        merged[diff_column] = merged[column] - merged[f"{column}_OPP"]
        diff_feature_columns.append(diff_column)

    modelling_columns = [
        "GAME_ID",
        "GAME_DATE",
        "TEAM_ABBREVIATION",
        "OPPONENT_ABBREVIATION",
        "HOME",
        "WIN",
        *diff_feature_columns,
    ]

    matchup_df = merged[modelling_columns].copy()
    matchup_df["HOME"] = matchup_df["HOME"].astype(int)

    return matchup_df, tuple(diff_feature_columns)


def compute_team_season_averages(
    team_games: TeamGameFeatures,
    weight_by_minutes: bool = False,
) -> pd.DataFrame:
    """Compute season-level average statistics for each team.

    Parameters
    ----------
    team_games:
        Team-level game dataframe produced by
        :func:`prepare_team_game_features`.
    weight_by_minutes:
        When ``True`` percentages are weighted by the total minutes played in
        the game. This can slightly stabilise season averages when rotations
        fluctuate.
    """

    df = team_games.data
    feature_columns = list(team_games.feature_columns)

    grouped = df.groupby("TEAM_ABBREVIATION")

    if weight_by_minutes and "MIN" in feature_columns:
        def weighted_mean(group):
            weights = group["MIN"].clip(lower=1)
            weighted = group[feature_columns].mul(weights, axis=0)
            return weighted.sum() / weights.sum()

        season_averages = grouped.apply(weighted_mean)
    else:
        season_averages = grouped[feature_columns].mean()

    season_averages.sort_index(inplace=True)
    return season_averages


def build_season_matchup_frame(
    season_averages: pd.DataFrame,
    diff_feature_columns: Sequence[str],
    team: str,
    opponent: str,
    home: bool,
) -> pd.DataFrame:
    """Create a single-row dataframe suitable for :class:`MatchupPredictor`.

    The resulting dataframe mirrors the structure of the training dataset with
    ``*_DIFF`` feature columns and a ``HOME`` indicator.
    """

    base_features = [col.replace("_DIFF", "") for col in diff_feature_columns]

    missing = {team, opponent} - set(season_averages.index)
    if missing:
        raise ValueError(
            "Season averages missing for teams: " + ", ".join(sorted(missing))
        )

    team_vector = season_averages.loc[team, base_features]
    opponent_vector = season_averages.loc[opponent, base_features]

    data = {
        diff_column: team_vector[base] - opponent_vector[base]
        for diff_column, base in zip(diff_feature_columns, base_features)
    }
    data["HOME"] = int(home)
    data["WIN"] = 0  # placeholder target column for API consistency
    data["GAME_ID"] = "SEASON_AVG"
    data["GAME_DATE"] = pd.Timestamp.utcnow()
    data["TEAM_ABBREVIATION"] = team
    data["OPPONENT_ABBREVIATION"] = opponent

    columns = [
        "GAME_ID",
        "GAME_DATE",
        "TEAM_ABBREVIATION",
        "OPPONENT_ABBREVIATION",
        "HOME",
        "WIN",
        *diff_feature_columns,
    ]

    return pd.DataFrame([data], columns=columns)
