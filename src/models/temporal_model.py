"""
temporal_model.py
------------------
Part 2: Attention Temporal Graph Convolutional Network (A3TGCN)
for time-evolving fraud detection.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from sklearn.metrics import roc_auc_score, average_precision_score
from torch_geometric_temporal.nn.recurrent import A3TGCN
from torch_geometric_temporal.signal import DynamicGraphTemporalSignal
import logging

logger = logging.getLogger(__name__)


class A3TGCNFraudModel(nn.Module):
    """
    Attention Temporal GCN for fraud detection on dynamic graphs.

    Architecture:
    - A3TGCN: captures temporal attention over graph snapshots
    - BatchNorm + ReLU + Dropout for regularization
    - Linear head for binary fraud classification
    - Returns both logits and embeddings
    """

    def __init__(self, node_features: int, hidden_dim: int = 64,
                 periods: int = 1, dropout: float = 0.3):
        super().__init__()
        self.tgnn    = A3TGCN(in_channels=node_features, out_channels=hidden_dim, periods=periods)
        self.bn      = nn.BatchNorm1d(hidden_dim)
        self.dropout = nn.Dropout(dropout)
        self.linear  = nn.Linear(hidden_dim, 1)

    def forward(self, x: torch.Tensor, edge_index: torch.Tensor,
                edge_weight: torch.Tensor = None):
        """
        Parameters
        ----------
        x : Tensor (num_nodes, node_features, periods)
        edge_index : Tensor (2, num_edges)
        edge_weight : Tensor (num_edges,), optional

        Returns
        -------
        logits (num_nodes,), embeddings (num_nodes, hidden_dim)
        """
        h = self.tgnn(x, edge_index, edge_weight)
        h = self.bn(h)
        h = F.relu(h)
        h = self.dropout(h)
        out = self.linear(h)
        return out.view(-1), h

    def get_embeddings(self, x: torch.Tensor, edge_index: torch.Tensor,
                       edge_weight: torch.Tensor = None) -> torch.Tensor:
        """Return raw hidden-layer embeddings (no classification head)."""
        h = self.tgnn(x, edge_index, edge_weight)
        return h


class TemporalTrainer:
    """
    Trainer for the A3TGCN temporal model.
    Supports early stopping and temporal train/test evaluation.
    """

    def __init__(self, model: A3TGCNFraudModel, device: str, config: dict):
        self.model  = model.to(device)
        self.device = device
        self.cfg    = config["temporal"]
        self.best_state   = None
        self.best_auroc   = 0.0

        self.optimizer = torch.optim.Adam(
            model.parameters(),
            lr=self.cfg["lr"],
            weight_decay=self.cfg["weight_decay"],
        )
        self.criterion = nn.BCEWithLogitsLoss()

    def _snapshot_to_tensors(self, snapshot):
        x  = torch.tensor(snapshot.x, dtype=torch.float32).unsqueeze(-1).to(self.device)
        ei = torch.tensor(snapshot.edge_index, dtype=torch.long).to(self.device)
        y  = torch.tensor(snapshot.y, dtype=torch.float32).to(self.device)
        return x, ei, y

    def train(self, train_dataset: DynamicGraphTemporalSignal,
              save_path: str = "artifacts/temporal_best.pth"):
        patience_counter = 0
        patience = self.cfg["patience"]
        epochs   = self.cfg["epochs"]

        logger.info("Training A3TGCN temporal model...")

        for epoch in range(1, epochs + 1):
            self.model.train()
            epoch_loss, all_preds, all_labels = 0.0, [], []

            for snapshot in train_dataset:
                x, ei, y = self._snapshot_to_tensors(snapshot)
                self.optimizer.zero_grad()
                logits, _ = self.model(x, ei)
                loss = self.criterion(logits, y)
                loss.backward()
                self.optimizer.step()
                epoch_loss += loss.item()
                all_preds.extend(torch.sigmoid(logits).detach().cpu().numpy())
                all_labels.extend(y.cpu().numpy())

            try:
                auroc = roc_auc_score(all_labels, all_preds)
                auprc = average_precision_score(all_labels, all_preds)
            except ValueError:
                auroc, auprc = 0.0, 0.0

            if epoch % 5 == 0:
                logger.info(
                    f"Epoch {epoch:03d}/{epochs} | "
                    f"Loss {epoch_loss/train_dataset.snapshot_count:.4f} | "
                    f"AUROC {auroc:.4f} | AUPRC {auprc:.4f}"
                )

            if auroc > self.best_auroc:
                self.best_auroc = auroc
                self.best_state = {k: v.clone() for k, v in self.model.state_dict().items()}
                torch.save(self.best_state, save_path)
                patience_counter = 0
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    logger.info(f"Early stopping at epoch {epoch}.")
                    break

        self.model.load_state_dict(self.best_state)
        logger.info(f"Best Train AUROC: {self.best_auroc:.4f}")
        return self.model

    def evaluate(self, test_dataset: DynamicGraphTemporalSignal) -> dict:
        """Evaluate on future (unseen) temporal snapshots."""
        self.model.eval()
        all_preds, all_labels = [], []

        with torch.no_grad():
            for snapshot in test_dataset:
                x, ei, y = self._snapshot_to_tensors(snapshot)
                logits, _ = self.model(x, ei)
                all_preds.extend(torch.sigmoid(logits).cpu().numpy())
                all_labels.extend(y.cpu().numpy())

        return {
            "auroc": roc_auc_score(all_labels, all_preds),
            "auprc": average_precision_score(all_labels, all_preds),
        }

    def extract_embeddings(self, dataset: DynamicGraphTemporalSignal,
                           snapshot_idx: int = -1) -> np.ndarray:
        """Extract embeddings from a specific snapshot (default: last)."""
        self.model.eval()
        features    = dataset.features
        edge_indices = dataset.edge_indices
        idx = snapshot_idx % len(features)

        x  = torch.tensor(features[idx], dtype=torch.float32).unsqueeze(-1).to(self.device)
        ei = torch.tensor(edge_indices[idx], dtype=torch.long).to(self.device)

        with torch.no_grad():
            emb = self.model.get_embeddings(x, ei).cpu().numpy()
        return emb
