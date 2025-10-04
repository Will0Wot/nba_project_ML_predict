# Continuing the NBA Matchup Prediction Engine

This guide helps developers understand the current state of the project, how to
work with the codebase, and where to focus when extending the matchup prediction
engine. It also highlights the biggest limitations you should address when
planning future iterations.

## Project recap

The repository contains a Python package, `nba_predictor`, that trains a
logistic regression model on 2021-22 NBA player game logs. The workflow
aggregates player statistics into matchup-level features, fits the model, and
exposes a command-line interface (CLI) that reports win probabilities and
feature contributions for a requested matchup.

Key modules:

- `nba_predictor.data` handles data loading, feature engineering, and creation
  of chronological train/test splits.
- `nba_predictor.model` defines the `MatchupPredictor` class that wraps the
  scikit-learn model, scaling pipeline, evaluation helpers, and explanation
  logic.
- `nba_predictor.main` provides the CLI entry point for training, evaluation,
  and matchup probability queries.

Supporting assets include historical player logs under `player_game_logs_2022.csv`
and pre-trained artifacts (`nba_model.pkl`, `le_team.pkl`, `le_matchup.pkl`) that
illustrate the expected file formats.

## Getting set up

1. **Create a virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the CLI** to reproduce the baseline workflow:

   ```bash
   python -m nba_predictor.main --team TOR --opponent MIL --home
   ```

   The command trains a model on the historical logs, evaluates it on the
   holdout split, and prints the win probability plus the top contributing
   features for the matchup.

Refer to `python -m nba_predictor.main --help` for optional arguments such as
`--weight-by-minutes` (minute-weighted season averages) or `--top-n` (number of
feature contributions to display).

## Extending the engine

To build on the current implementation, consider the following focus areas:

### Data updates and ingestion

- Replace or augment `player_game_logs_2022.csv` with newer seasons.
- Integrate injuries, betting lines, rest days, or travel schedules as additional
  features.
- Support live data ingestion through the NBA stats API; adapt `nba_predictor.data`
  to cache and preprocess the responses.

### Modelling improvements

- Experiment with gradient boosted trees, neural networks, or Bayesian models by
  extending `MatchupPredictor` or adding new classes under `nba_predictor.model`.
- Incorporate hyperparameter tuning (e.g., scikit-learn's `GridSearchCV`).
- Explore calibration techniques to improve probability quality.

### Evaluation and monitoring

- Implement backtesting across multiple seasons with rolling retraining.
- Add richer metrics such as Brier score, log-loss, or betting-focused
  profitability analyses.
- Build dashboards or notebooks that track model drift when new data is added.

### Productization

- Wrap the CLI in a REST API (FastAPI or Flask) for integration with other tools.
- Provide a simple front-end to explore matchups and player prop insights.
- Containerize the application with Docker for reproducible deployments.

## Limitations to address

- **Data coverage**: Only 2021-22 season game logs are bundled. Predictions for
  later seasons require updated data and possibly re-training to account for
  roster changes. The CLI now falls back to league-average vectors when a team
  is missing, but high-quality forecasts still depend on ingesting those teams'
  actual logs.
- **Model simplicity**: Logistic regression assumes linear relationships and may
  miss interaction effects between players, lineups, or contextual factors.
- **Feature granularity**: The current features aggregate per-team season
  averages. They do not capture lineup combinations, clutch performance, or
  defensive matchups between specific players.
- **Injury and availability data**: The engine does not account for player
  injuries, rest days, or minute restrictions.
- **Real-time adaptability**: There is no automation around pulling fresh data,
  re-training models, or validating predictions in production environments.

Addressing these limitations will significantly improve accuracy and usability
for bettors, analysts, and fans.

## Suggested next steps

1. Refresh the dataset with the most recent season and re-train the model.
2. Add player availability tracking and adjust feature engineering accordingly.
3. Evaluate alternative models and benchmark them against the logistic regression
   baseline.
4. Build automated tests that validate data integrity and model performance.
5. Plan for deployment by packaging the model behind an API or simple web UI.

Following this roadmap will gradually evolve the project from a prototype into a
more robust NBA matchup prediction platform.
