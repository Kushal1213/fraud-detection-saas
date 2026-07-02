"""
metrics.py
----------
Evaluation helpers: AUROC, AUPRC, Precision@K, and a combined reporter.
"""

import numpy as np
from sklearn.metrics import (
    roc_auc_score, average_precision_score,
    precision_score, recall_score, f1_score,
)
import logging

logger = logging.getLogger(__name__)


def auroc(y_true: np.ndarray, y_score: np.ndarray) -> float:
    return roc_auc_score(y_true, y_score)


def auprc(y_true: np.ndarray, y_score: np.ndarray) -> float:
    return average_precision_score(y_true, y_score)


def precision_at_k(y_true: np.ndarray, y_score: np.ndarray, k: int = 100) -> float:
    """
    Fraction of fraud cases in the top-K highest-scored predictions.
    Equivalent to Precision@K used in the README comparison table.
    """
    top_k = np.argsort(y_score)[::-1][:k]
    return y_true[top_k].mean()


def report(y_true: np.ndarray, y_score: np.ndarray,
           threshold: float = 0.5, k: int = 100) -> dict:
    """Compute and log a full set of metrics."""
    y_pred = (y_score >= threshold).astype(int)
    metrics = {
        "auroc":        auroc(y_true, y_score),
        "auprc":        auprc(y_true, y_score),
        "precision_at_k": precision_at_k(y_true, y_score, k),
        "precision":    precision_score(y_true, y_pred, zero_division=0),
        "recall":       recall_score(y_true, y_pred, zero_division=0),
        "f1":           f1_score(y_true, y_pred, zero_division=0),
    }
    logger.info(
        f"AUROC {metrics['auroc']:.4f} | AUPRC {metrics['auprc']:.4f} | "
        f"P@{k} {metrics['precision_at_k']:.4f} | F1 {metrics['f1']:.4f}"
    )
    return metrics
