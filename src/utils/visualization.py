"""
visualization.py
----------------
ROC curves, PR curves, confusion matrix, and model comparison bar chart.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import roc_curve, precision_recall_curve, confusion_matrix
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
sns.set_theme(style="whitegrid")


def _save(fig, path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Plot saved to {path}")


def plot_roc_pr(y_true: np.ndarray, y_scores: dict,
                save_path: str = "artifacts/roc_pr.png"):
    """
    Parameters
    ----------
    y_scores : dict mapping model_name → score array
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    for name, scores in y_scores.items():
        fpr, tpr, _ = roc_curve(y_true, scores)
        axes[0].plot(fpr, tpr, label=name)

        prec, rec, _ = precision_recall_curve(y_true, scores)
        axes[1].plot(rec, prec, label=name)

    axes[0].set(title="ROC Curve", xlabel="FPR", ylabel="TPR")
    axes[0].plot([0, 1], [0, 1], "k--")
    axes[0].legend()

    axes[1].set(title="Precision-Recall Curve", xlabel="Recall", ylabel="Precision")
    axes[1].legend()

    fig.tight_layout()
    _save(fig, save_path)


def plot_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray,
                          save_path: str = "artifacts/confusion.png"):
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=["Legit", "Fraud"],
                yticklabels=["Legit", "Fraud"], ax=ax)
    ax.set(title="Confusion Matrix", xlabel="Predicted", ylabel="Actual")
    fig.tight_layout()
    _save(fig, save_path)


def plot_model_comparison(results: dict, metric: str = "auroc",
                          save_path: str = "artifacts/model_comparison.png"):
    """
    Parameters
    ----------
    results : dict mapping model_name → metrics dict
    """
    names  = list(results.keys())
    values = [results[n][metric] for n in names]

    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.barh(names, values, color=sns.color_palette("muted", len(names)))
    ax.set(title=f"Model Comparison — {metric.upper()}",
           xlabel=metric.upper(), xlim=(min(values) * 0.95, 1.0))
    for bar, val in zip(bars, values):
        ax.text(val + 0.002, bar.get_y() + bar.get_height() / 2,
                f"{val:.4f}", va="center", fontsize=9)
    fig.tight_layout()
    _save(fig, save_path)
