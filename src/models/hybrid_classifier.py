"""
hybrid_classifier.py
---------------------
Hybrid fraud detector: fuses GNN node embeddings with
tabular features, then trains XGBoost for final classification.
"""

import numpy as np
import xgboost as xgb
from sklearn.metrics import (
    roc_auc_score, average_precision_score,
    precision_score, recall_score, f1_score,
    classification_report, confusion_matrix,
)
from sklearn.model_selection import train_test_split
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class HybridFraudDetector:
    """
    Combines GNN embeddings with raw tabular features into a
    high-dimensional input for an XGBoost classifier.

    Pipeline:
        tabular_features (N x T) + gnn_embeddings (N x E)
                         ↓
              XGBoost classifier (N x (T+E))
    """

    def __init__(self, config: dict):
        self.cfg = config["xgboost"]
        self.model = None

    def build_features(self, tabular: np.ndarray,
                       embeddings: np.ndarray) -> np.ndarray:
        """Concatenate tabular and GNN embedding features."""
        n = min(len(tabular), len(embeddings))
        if embeddings.ndim == 1:
            embeddings = embeddings.reshape(-1, 1)
        X = np.hstack([tabular[:n], embeddings[:n]])
        logger.info(f"Hybrid feature matrix: {X.shape}")
        return X

    def fit(self, X: np.ndarray, y: np.ndarray,
            X_val: np.ndarray = None, y_val: np.ndarray = None):
        """Train XGBoost classifier with optional validation for early stopping."""
        scale_pos_weight = (y == 0).sum() / max((y == 1).sum(), 1)
        logger.info(f"scale_pos_weight = {scale_pos_weight:.2f}")

        self.model = xgb.XGBClassifier(
            n_estimators=self.cfg["n_estimators"],
            max_depth=self.cfg["max_depth"],
            learning_rate=self.cfg["learning_rate"],
            subsample=self.cfg["subsample"],
            colsample_bytree=self.cfg["colsample_bytree"],
            scale_pos_weight=scale_pos_weight,
            eval_metric=self.cfg["eval_metric"],
            tree_method=self.cfg.get("tree_method", "hist"),
            random_state=42,
            use_label_encoder=False,
        )

        fit_kwargs = {"X": X, "y": y, "verbose": False}
        if X_val is not None:
            fit_kwargs["eval_set"] = [(X, y), (X_val, y_val)]
            fit_kwargs["early_stopping_rounds"] = self.cfg["early_stopping_rounds"]

        logger.info("Training XGBoost hybrid classifier...")
        self.model.fit(**fit_kwargs)
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)[:, 1]

    def evaluate(self, X: np.ndarray, y: np.ndarray,
                 threshold: float = 0.5) -> dict:
        """Full evaluation with AUROC, AUPRC, F1, precision, recall."""
        proba  = self.predict_proba(X)
        y_pred = (proba >= threshold).astype(int)

        metrics = {
            "auroc":     roc_auc_score(y, proba),
            "auprc":     average_precision_score(y, proba),
            "precision": precision_score(y, y_pred, zero_division=0),
            "recall":    recall_score(y, y_pred, zero_division=0),
            "f1":        f1_score(y, y_pred, zero_division=0),
            "conf_matrix": confusion_matrix(y, y_pred),
        }
        logger.info(
            f"AUROC {metrics['auroc']:.4f} | AUPRC {metrics['auprc']:.4f} | "
            f"F1 {metrics['f1']:.4f}"
        )
        print(classification_report(y, y_pred, digits=4))
        return metrics

    def save(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.model.save_model(path)
        logger.info(f"XGBoost model saved to {path}")

    @classmethod
    def load(cls, model_path: str, config: dict) -> "HybridFraudDetector":
        instance = cls(config)
        instance.model = xgb.XGBClassifier()
        instance.model.load_model(model_path)
        return instance
