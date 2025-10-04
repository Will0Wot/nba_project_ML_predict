# NBA Matchup Prediction Engine

This project provides a small Python package for analysing NBA player game logs
and building a matchup-level model that estimates the probability of a team
winning against a specific opponent. The workflow extracts team strengths from
player level statistics, trains a logistic regression model and produces
actionable insights about the most important matchup factors.

## Getting started

1. Create a virtual environment and install the dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Run the command line interface to train the model and evaluate its
   performance using the included 2022 player game logs:

   ```bash
   python -m nba_predictor.main
   ```

   The script performs a chronological train/test split, fits a logistic
   regression model and prints evaluation metrics.

3. Generate a probability estimate for a specific matchup by providing the team
   abbreviations. The engine will construct season-average feature vectors for
   each side, compute the win probability for the selected team and display the
   features that influenced the prediction the most.

   ```bash
   python -m nba_predictor.main --team TOR --opponent BOS --home
   ```

   Use the `--weight-by-minutes` flag to weight season averages by minutes
   played, and `--top-n` to control how many feature contributions are shown in
   the explanation output.

4. Build the supporting visuals that drive the storytelling deck (and optionally
   produce a PDF-ready summary). You can either invoke the package module
   directly or rely on the compatibility wrapper under `root/`:

   ```bash
   python -m nba_predictor.visualization \
       --player-logs player_game_logs_2022.csv \
       --pdf reports/summary.pdf
   ```

   The command saves four PNG charts under `reports/figures/`, covering team
   offense vs. defense, home-court advantage, the leading scorers, and the
   assist-to-turnover landscape. When `--pdf` is supplied, those visuals are
   combined with the narrative in [`DATA_STORY.md`](DATA_STORY.md) to produce a
   presentation-ready deck (defaulting to `reports/summary.pdf`). Supply a
   custom markdown file with `--story-file` if you want to swap in different
   talking points. The `reports/` directory and generated PDF are now excluded
   from version control, so create the folder locally before running the
   command and treat the output as an ephemeral artifact that you regenerate on
   demand. Running `python root/visualization.py` forwards the same arguments to
   the package CLI; this is provided to match earlier instructions that
   referenced the script directly.

## Package overview

- `nba_predictor.data`: Loading player logs, aggregating them into team game
  features and building matchup datasets ready for modelling.
- `nba_predictor.model`: A `MatchupPredictor` class that wraps a logistic
  regression model, scales features, evaluates performance and provides linear
  explanations for predictions.
- `nba_predictor.main`: Command line entry point that orchestrates the full
  pipeline and offers an interactive way to explore matchups.

The code is intentionally modular so it can be extended with alternative models
or additional data sources (e.g. betting lines, injury reports) to enhance
prediction accuracy and player prop analysis.
