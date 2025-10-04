"""Visualization utilities for exploring NBA matchup data."""
from __future__ import annotations

import argparse
import textwrap
from pathlib import Path
from typing import Iterable, Optional, Tuple

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd

from .data import TeamGameFeatures, load_player_logs, prepare_team_game_features


def _attach_opponent_points(team_games: pd.DataFrame) -> pd.DataFrame:
    """Add opponent points for each team game."""

    opponent_points = (
        team_games[["GAME_ID", "TEAM_ABBREVIATION", "PTS"]]
        .rename(
            columns={
                "TEAM_ABBREVIATION": "OPPONENT_ABBREVIATION",
                "PTS": "OPP_POINTS",
            }
        )
        .copy()
    )

    enriched = team_games.merge(
        opponent_points,
        on=["GAME_ID", "OPPONENT_ABBREVIATION"],
        how="left",
        validate="many_to_one",
    )
    enriched = enriched.dropna(subset=["OPP_POINTS"]).copy()
    enriched["OPP_POINTS"] = enriched["OPP_POINTS"].astype(float)
    enriched["POINT_DIFFERENTIAL"] = enriched["PTS"] - enriched["OPP_POINTS"]
    return enriched


def compute_team_summaries(team_games: pd.DataFrame) -> pd.DataFrame:
    """Compute per-team summary statistics from team game data."""

    team_summary = (
        team_games.groupby("TEAM_ABBREVIATION")
        .agg(
            games_played=("GAME_ID", "nunique"),
            avg_points=("PTS", "mean"),
            avg_points_allowed=("OPP_POINTS", "mean"),
            avg_point_diff=("POINT_DIFFERENTIAL", "mean"),
            avg_rebounds=("REB", "mean"),
            avg_assists=("AST", "mean"),
            avg_turnovers=("TOV", "mean"),
            win_rate=("WIN", "mean"),
        )
        .sort_values("avg_point_diff", ascending=False)
    )
    team_summary["net_rating"] = team_summary["avg_point_diff"]
    turnovers = team_summary["avg_turnovers"].replace(0, pd.NA)
    team_summary["assist_to_turnover"] = team_summary["avg_assists"] / turnovers
    return team_summary


def compute_home_away_summary(team_games: pd.DataFrame) -> pd.DataFrame:
    """Compute win rates split by home/away."""

    summary = (
        team_games.groupby(["TEAM_ABBREVIATION", "HOME"])
        .agg(win_rate=("WIN", "mean"), games=("GAME_ID", "nunique"))
        .reset_index()
    )
    pivot = summary.pivot(
        index="TEAM_ABBREVIATION", columns="HOME", values="win_rate"
    ).rename(columns={False: "away_win_rate", True: "home_win_rate"})
    pivot["home_court_edge"] = pivot["home_win_rate"] - pivot["away_win_rate"]
    return pivot.sort_values("home_court_edge", ascending=False)


def compute_player_scoring(player_logs: pd.DataFrame, top_n: int = 12) -> pd.DataFrame:
    """Return the top N scorers by average points per game."""

    scoring = (
        player_logs.groupby("PLAYER_NAME")
        .agg(
            avg_points=("PTS", "mean"),
            avg_minutes=("MIN", "mean"),
            games_played=("GAME_ID", "nunique"),
            team=("TEAM_ABBREVIATION", lambda x: x.mode().iat[0] if not x.mode().empty else ""),
        )
        .query("games_played >= 10")
        .sort_values("avg_points", ascending=False)
        .head(top_n)
    )
    scoring["label"] = scoring.index + " (" + scoring["team"] + ")"
    return scoring


def create_offense_defense_plot(team_summary: pd.DataFrame, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 7))
    scatter = ax.scatter(
        team_summary["avg_points"],
        team_summary["avg_points_allowed"],
        c=team_summary["net_rating"],
        cmap="RdYlGn",
        s=150,
        edgecolors="black",
        linewidths=0.5,
    )
    for team, row in team_summary.iterrows():
        ax.annotate(
            team,
            (row["avg_points"], row["avg_points_allowed"]),
            textcoords="offset points",
            xytext=(5, -5),
            fontsize=8,
        )
    ax.set_title("Team scoring vs. points allowed")
    ax.set_xlabel("Average points scored")
    ax.set_ylabel("Average points allowed")
    colorbar = fig.colorbar(scatter, ax=ax)
    colorbar.set_label("Net rating (points per game differential)")
    ax.invert_yaxis()
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def create_home_court_plot(home_away: pd.DataFrame, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 7))
    teams = home_away.index
    ax.barh(teams, home_away["home_court_edge"], color="#1f77b4")
    ax.set_xlabel("Home win rate - Away win rate")
    ax.set_title("Home court advantage by team")
    ax.axvline(0, color="black", linewidth=0.8)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def create_player_scoring_plot(player_scoring: pd.DataFrame, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(
        player_scoring["label"],
        player_scoring["avg_points"],
        color="#ff7f0e",
        alpha=0.85,
    )
    ax.set_xlabel("Average points per game")
    ax.set_title("Top scorers in the dataset")
    ax.invert_yaxis()
    for index, value in enumerate(player_scoring["avg_points"]):
        ax.text(value + 0.2, index, f"{value:.1f} ppg", va="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def create_assist_turnover_plot(team_summary: pd.DataFrame, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.scatter(
        team_summary["avg_assists"],
        team_summary["avg_turnovers"],
        s=120,
        c=team_summary["assist_to_turnover"],
        cmap="Blues",
        edgecolors="black",
        linewidths=0.5,
    )
    for team, row in team_summary.iterrows():
        ax.annotate(
            team,
            (row["avg_assists"], row["avg_turnovers"]),
            textcoords="offset points",
            xytext=(5, -5),
            fontsize=8,
        )
    ax.set_xlabel("Average assists")
    ax.set_ylabel("Average turnovers")
    ax.set_title("Ball movement vs. ball security")
    colorbar = plt.colorbar(ax.collections[0], ax=ax)
    colorbar.set_label("Assist-to-turnover ratio")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def _render_story_to_pdf(story_path: Path, pdf: PdfPages) -> None:
    """Render the markdown story into one or more PDF pages."""

    text = story_path.read_text(encoding="utf-8")

    fig = plt.figure(figsize=(8.5, 11))
    fig.patch.set_facecolor("white")
    y = 0.92
    has_content = False

    def flush_page() -> None:
        nonlocal fig, y, has_content
        if has_content:
            pdf.savefig(fig)
        plt.close(fig)
        fig = plt.figure(figsize=(8.5, 11))
        fig.patch.set_facecolor("white")
        y = 0.92
        has_content = False
        return None

    for line in text.splitlines():
        stripped = line.strip()

        if not stripped:
            y -= 0.02
            if y < 0.12:
                flush_page()
            continue

        if stripped.startswith("!"):
            # Images are embedded as separate charts later in the PDF.
            continue

        has_content = True

        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            content = stripped[level:].strip()
            if level == 1:
                fontsize = 20
                delta = 0.08
            elif level == 2:
                fontsize = 16
                delta = 0.06
            else:
                fontsize = 14
                delta = 0.05
            fig.text(0.05, y, content, fontsize=fontsize, fontweight="bold")
            y -= delta
        elif stripped.startswith("* "):
            bullet = stripped[2:].strip()
            wrapped = textwrap.wrap(bullet, width=85)
            for i, segment in enumerate(wrapped):
                prefix = "• " if i == 0 else "  "
                fig.text(0.07, y, prefix + segment, fontsize=11)
                y -= 0.032
            y -= 0.008
        else:
            wrapped = textwrap.wrap(stripped, width=90)
            for segment in wrapped:
                fig.text(0.05, y, segment, fontsize=12)
                y -= 0.035
            y -= 0.01

        if y < 0.12:
            flush_page()

    if has_content:
        pdf.savefig(fig)
    plt.close(fig)


def _embed_charts_in_pdf(chart_paths: Iterable[Path], pdf: PdfPages) -> None:
    """Embed saved chart images into the PDF summary."""

    for chart_path in chart_paths:
        fig = plt.figure(figsize=(11, 8.5))
        fig.patch.set_facecolor("white")
        ax = fig.add_subplot(111)
        image = mpimg.imread(chart_path)
        ax.imshow(image)
        ax.axis("off")
        fig.suptitle(chart_path.stem.replace("_", " ").title(), fontsize=16, y=0.98)
        pdf.savefig(fig)
        plt.close(fig)


def _create_pdf_summary(
    chart_paths: Tuple[Path, ...], story_path: Optional[Path], pdf_path: Path
) -> None:
    """Create a PDF that stitches together charts and the written story."""

    with PdfPages(pdf_path) as pdf:
        # Cover page
        cover = plt.figure(figsize=(8.5, 11))
        cover.patch.set_facecolor("white")
        cover.text(
            0.5,
            0.85,
            "NBA Matchup Prediction Project",
            fontsize=22,
            ha="center",
            fontweight="bold",
        )
        cover.text(
            0.5,
            0.78,
            "Visual and narrative summary",
            fontsize=16,
            ha="center",
        )
        cover.text(
            0.1,
            0.68,
            "This PDF stitches together the exploratory charts generated by the visualization\n"
            "module with the narrative from DATA_STORY.md so you can quickly share the\n"
            "state of the dataset, model focus areas, and current limitations.",
            fontsize=12,
        )
        pdf.savefig(cover)
        plt.close(cover)

        _embed_charts_in_pdf(chart_paths, pdf)

        if story_path and story_path.exists():
            _render_story_to_pdf(story_path, pdf)


def generate_visualizations(
    player_logs_path: Path,
    output_dir: Path,
    top_players: int,
    story_path: Optional[Path] = None,
    pdf_path: Optional[Path] = None,
) -> Tuple[Path, ...]:
    player_logs = load_player_logs(player_logs_path)
    team_features: TeamGameFeatures = prepare_team_game_features(player_logs)
    team_games = _attach_opponent_points(team_features.data)

    team_summary = compute_team_summaries(team_games)
    home_away = compute_home_away_summary(team_games)
    player_scoring = compute_player_scoring(player_logs, top_players)

    output_dir.mkdir(parents=True, exist_ok=True)

    offense_defense_path = output_dir / "team_offense_defense.png"
    home_court_path = output_dir / "home_court_advantage.png"
    scoring_path = output_dir / "top_scorers.png"
    assist_turnover_path = output_dir / "assist_turnover_balance.png"

    create_offense_defense_plot(team_summary, offense_defense_path)
    create_home_court_plot(home_away, home_court_path)
    create_player_scoring_plot(player_scoring, scoring_path)
    create_assist_turnover_plot(team_summary, assist_turnover_path)

    chart_paths = (
        offense_defense_path,
        home_court_path,
        scoring_path,
        assist_turnover_path,
    )

    if pdf_path is not None:
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        _create_pdf_summary(chart_paths, story_path, pdf_path)

    return chart_paths


def main(argv: Optional[Iterable[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        description="Generate exploratory visualizations for NBA matchup data",
    )
    parser.add_argument(
        "--player-logs",
        type=Path,
        required=True,
        help="Path to the player logs CSV file",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/figures"),
        help="Directory where visualizations will be saved",
    )
    parser.add_argument(
        "--top-players",
        type=int,
        default=12,
        help="Number of top scorers to include in the player chart",
    )
    parser.add_argument(
        "--story-file",
        type=Path,
        default=None,
        help=(
            "Optional markdown file describing the visuals. If provided, the text will "
            "be embedded into the generated PDF summary. Defaults to DATA_STORY.md when "
            "present in the project root."
        ),
    )
    parser.add_argument(
        "--pdf",
        type=Path,
        default=None,
        help="Optional path where a combined PDF summary (charts + story) will be saved.",
    )

    args = parser.parse_args(argv)

    story_file = args.story_file
    if story_file is None:
        default_story = Path("DATA_STORY.md")
        story_file = default_story if default_story.exists() else None

    paths = generate_visualizations(
        args.player_logs,
        args.output_dir,
        args.top_players,
        story_file,
        args.pdf,
    )

    print("Generated visualizations:")
    for path in paths:
        print(f" - {path}")

    if args.pdf is not None:
        print(f"PDF summary saved to: {args.pdf}")


if __name__ == "__main__":
    main()
