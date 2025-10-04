"""Modelling utilities for predicting NBA matchup outcomes."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss, roc_auc_score
from sklearn.preprocessing import StandardScaler


@dataclass
class EvaluationResult:
    """Container for evaluation metrics."""

    accuracy: float
    log_loss: float
    roc_auc: float

    def as_dict(self) -> Mapping[str, float]:
        return {
            "accuracy": float(self.accuracy),
            "log_loss": float(self.log_loss),
            "roc_auc": float(self.roc_auc),
        }


class MatchupPredictor:
    """Predict the probability of a team winning an NBA matchup."""

    def __init__(
        self,
        feature_columns: Sequence[str] | None = None,
        model: LogisticRegression | None = None,
    ) -> None:
        self.feature_columns: Sequence[str] | None = feature_columns
        self.model = model or LogisticRegression(max_iter=1000)
        self.scaler = StandardScaler()

    def _prepare_features(self, dataframe: pd.DataFrame) -> np.ndarray:
        if not self.feature_columns:
            raise ValueError("Feature columns have not been set. Call `fit` first.")
        missing = set(self.feature_columns) - set(dataframe.columns)
        if missing:
            raise KeyError(
                "Missing required feature columns: " + ", ".join(sorted(missing))
            )
        features = dataframe.loc[:, self.feature_columns].fillna(0.0)
        return self.scaler.transform(features)

    def fit(self, dataframe: pd.DataFrame, feature_columns: Sequence[str]) -> "MatchupPredictor":
        """Fit the underlying model using the provided matchup dataframe."""

        self.feature_columns = tuple(feature_columns)
        features = dataframe.loc[:, self.feature_columns].fillna(0.0)
        targets = dataframe["WIN"].astype(int)

        scaled_features = self.scaler.fit_transform(features)
        self.model.fit(scaled_features, targets)
        return self

    def predict_proba(self, dataframe: pd.DataFrame) -> pd.Series:
        """Return win probability estimates for each row in ``dataframe``."""

        probabilities = self.model.predict_proba(self._prepare_features(dataframe))[:, 1]
        return pd.Series(probabilities, index=dataframe.index, name="win_probability")

    def predict(self, dataframe: pd.DataFrame, threshold: float = 0.5) -> pd.Series:
        """Return binary win/loss predictions using a probability threshold."""

        probabilities = self.predict_proba(dataframe)
        return (probabilities >= threshold).astype(int)

    def evaluate(self, dataframe: pd.DataFrame) -> EvaluationResult:
        """Compute accuracy, log-loss and ROC AUC on the provided dataset."""

        y_true = dataframe["WIN"].astype(int)
        probabilities = self.predict_proba(dataframe)
        predictions = (probabilities >= 0.5).astype(int)

        return EvaluationResult(
            accuracy=accuracy_score(y_true, predictions),
            log_loss=log_loss(y_true, probabilities, labels=[0, 1]),
            roc_auc=roc_auc_score(y_true, probabilities),
        )

    def explain(self, dataframe: pd.DataFrame, top_n: int = 5) -> Sequence[Mapping[str, float]]:
        """Provide simple linear explanations for each matchup row.

        The explanation is derived from the logistic regression coefficients,
        highlighting which feature differences contributed most strongly to the
        predicted probability.
        """

        if self.feature_columns is None:
            raise ValueError("Predictor must be fitted before explanations are available.")

        if not hasattr(self.model, "coef_"):
            raise AttributeError("The underlying model does not expose coefficients.")

        coefs = self.model.coef_.ravel()
        probabilities = self.predict_proba(dataframe)
        feature_values = dataframe.loc[:, self.feature_columns].fillna(0.0)

        explanations = []
        for row_index, (row, probability) in enumerate(zip(feature_values.values, probabilities)):
            contributions = row * coefs
            sorted_indices = np.argsort(-np.abs(contributions))[:top_n]
            explanation = {
                self.feature_columns[i]: float(contributions[i]) for i in sorted_indices
            }
            explanation["probability"] = float(probability)
            explanations.append(explanation)
        return explanations
