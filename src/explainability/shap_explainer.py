""""
shap_explainer.py
-----------------
SHAP-based global and local interpretability for the hybrid XGBoost classifier.
"""

import numpy as np
import shap
import matplotlib.pyplot as plt
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class FraudExplainer:
    """
    Wraps shap.TreeExplainer around the XGBoost hybrid model.

    Usage
    -----
    explainer = FraudExplainer(model=detector.model, background_data=X_train)
    explainer.plot_global_importance(X_test)
    explainer.explain_prediction(X_test[42])
    """

    def __init__(self, model, background_data: np.ndarray,
                 feature_names: list = None):
        self.model         = model
        self.feature_names = feature_names
        logger.info("Building SHAP TreeExplainer...")
        self.explainer  = shap.TreeExplainer(model)
        self.shap_values = None

    # ------------------------------------------------------------------
    # Global explainability
    # ------------------------------------------------------------------

    def compute_shap_values(self, X: np.ndarray) -> np.ndarray:
        """Compute and cache SHAP values for X."""
        logger.info(f"Computing SHAP values for {len(X)} samples...")
        self.shap_values = self.explainer.shap_values(X)
        return self.shap_values

    def plot_global_importance(self, X: np.ndarray,
                               save_path: str = "artifacts/shap_global.png",
                               max_display: int = 20):
        """Summary beeswarm plot of global feature importance."""
        sv = self.compute_shap_values(X)
        plt.figure(figsize=(10, 8))
        shap.summary_plot(sv, X, feature_names=self.feature_names,
                          max_display=max_display, show=False)
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
        plt.close()
        logger.info(f"Global SHAP plot saved to {save_path}")

    def plot_bar_importance(self, X: np.ndarray,
                            save_path: str = "artifacts/shap_bar.png"):
        """Bar chart of mean absolute SHAP values."""
        sv = self.compute_shap_values(X)
        plt.figure(figsize=(10, 6))
        shap.summary_plot(sv, X, plot_type="bar",
                          feature_names=self.feature_names, show=False)
        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
        plt.close()

    # ------------------------------------------------------------------
    # Local explainability
    # ------------------------------------------------------------------

    def explain_prediction(self, x: np.ndarray,
                            save_path: str = "artifacts/shap_local.png"):
        """
        Waterfall / force plot for a single prediction.

        Parameters
        ----------
        x : 1-D array of shape (n_features,)
        """
        if x.ndim == 1:
            x = x.reshape(1, -1)
        sv = self.explainer.shap_values(x)[0]
        exp_val = self.explainer.expected_value

        plt.figure(figsize=(14, 4))
        shap.force_plot(exp_val, sv, x[0],
                        feature_names=self.feature_names,
                        matplotlib=True, show=False)
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close()
        logger.info(f"Local SHAP explanation saved to {save_path}")
        return sv

    def top_features(self, X: np.ndarray, n: int = 20) -> list:
        """Return top-n feature names sorted by mean |SHAP|."""
        sv = self.compute_shap_values(X)
        mean_abs = np.abs(sv).mean(axis=0)
        order    = np.argsort(mean_abs)[::-1][:n]
        if self.feature_names:
            return [(self.feature_names[i], mean_abs[i]) for i in order]
        return [(f"feature_{i}", mean_abs[i]) for i in order]
