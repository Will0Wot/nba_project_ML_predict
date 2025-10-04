"""NBA matchup prediction engine package."""
from .data import (
    TeamGameFeatures,
    build_matchup_dataset,
    build_season_matchup_frame,
    compute_team_season_averages,
    load_player_logs,
    prepare_team_game_features,
)
from .model import MatchupPredictor

__all__ = [
    "TeamGameFeatures",
    "load_player_logs",
    "prepare_team_game_features",
    "build_matchup_dataset",
    "compute_team_season_averages",
    "build_season_matchup_frame",
    "MatchupPredictor",
]
