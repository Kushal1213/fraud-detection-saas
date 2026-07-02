"""
graphsage_model.py
------------------
Part 1: Static GraphSAGE fraud detection model.
3-layer inductive GNN with BatchNorm, dropout, and BCEWithLogitsLoss.
"""

import torch
import torch.nn.functional as F
from torch_geometric.nn import SAGEConv
from torch_geometric.data import Data
import numpy as np
from sklearn.metrics import roc_auc_score, average_precision_score
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class FraudGraphSAGE(torch.nn.Module):
    """
    3-layer GraphSAGE with:
    - Batch normalization after each conv
    - Dropout between layers
    - Linear head for binary fraud classification
    """

    def __init__(self, in_channels: int, hidden_channels: int = 128,
                 num_layers: int = 3, dropout: float = 0.3):
        super().__init__()
        self.num_layers = num_layers
        self.dropout = dropout

        self.convs = torch.nn.ModuleList()
        self.bns   = torch.nn.ModuleList()

        self.convs.append(SAGEConv(in_channels, hidden_channels))
        self.bns.append(torch.nn.BatchNorm1d(hidden_channels))

        for _ in range(num_layers - 2):
            self.convs.append(SAGEConv(hidden_channels, hidden_channels))
            self.bns.append(torch.nn.BatchNorm1d(hidden_channels))

        self.convs.append(SAGEConv(hidden_channels, hidden_channels))
        self.bns.append(torch.nn.BatchNorm1d(hidden_channels))

        self.pred = torch.nn.Linear(hidden_channels, 1)

    def forward(self, data: Data) -> torch.Tensor:
        x, edge_index = data.x, data.edge_index
        for i in range(self.num_layers):
            x = self.convs[i](x, edge_index)
            x = self.bns[i](x)
            x = F.relu(x)
            if i < self.num_layers - 1:
                x = F.dropout(x, p=self.dropout, training=self.training)
        return self.pred(x).view(-1)

    def get_embeddings(self, data: Data) -> torch.Tensor:
        """Return penultimate-layer node embeddings (before the linear head)."""
        x, edge_index = data.x, data.edge_index
        for i in range(self.num_layers):
            x = self.convs[i](x, edge_index)
            x = self.bns[i](x)
            if i < self.num_layers - 1:
                x = F.relu(x)
        return x


class GraphSAGETrainer:
    """Trainer with early stopping for the static GraphSAGE model."""

    def __init__(self, model: FraudGraphSAGE, device: str, config: dict):
        self.model   = model.to(device)
        self.device  = device
        self.config  = config["graphsage"]
        self.best_val_auc = 0.0
        self.best_state   = None

        pos_weight = None  # set after data is available
        self.optimizer = torch.optim.Adam(
            model.parameters(),
            lr=self.config["lr"],
            weight_decay=self.config["weight_decay"],
        )

    def _build_criterion(self, data: Data) -> torch.nn.Module:
        pos_w = (
            (data.y[data.train_mask] == 0).sum().float()
            / (data.y[data.train_mask] == 1).sum().float()
        )
        return torch.nn.BCEWithLogitsLoss(
            pos_weight=pos_w.to(self.device)
        )

    def train(self, data: Data, save_path: str = "artifacts/graphsage_best.pth"):
        data = data.to(self.device)
        criterion = self._build_criterion(data)
        patience_counter = 0
        patience = self.config["patience"]
        epochs   = self.config["epochs"]

        logger.info("Training GraphSAGE...")
        for epoch in range(1, epochs + 1):
            self.model.train()
            self.optimizer.zero_grad()
            out  = self.model(data)
            loss = criterion(out[data.train_mask], data.y[data.train_mask])
            loss.backward()
            self.optimizer.step()

            self.model.eval()
            with torch.no_grad():
                logits = self.model(data)
                val_scores = torch.sigmoid(logits[data.val_mask]).cpu().numpy()
                val_labels = data.y[data.val_mask].cpu().numpy()
                val_auc    = roc_auc_score(val_labels, val_scores)

            if epoch % 10 == 0:
                logger.info(f"Epoch {epoch:03d} | Loss {loss:.4f} | Val AUROC {val_auc:.4f}")

            if val_auc > self.best_val_auc:
                self.best_val_auc = val_auc
                self.best_state   = {k: v.clone() for k, v in self.model.state_dict().items()}
                torch.save(self.best_state, save_path)
                patience_counter = 0
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    logger.info(f"Early stopping at epoch {epoch}.")
                    break

        self.model.load_state_dict(self.best_state)
        logger.info(f"Best Val AUROC: {self.best_val_auc:.4f}")
        return self.model

    def evaluate(self, data: Data) -> dict:
        data = data.to(self.device)
        self.model.eval()
        with torch.no_grad():
            out    = self.model(data)
            scores = torch.sigmoid(out[data.test_mask]).cpu().numpy()
            labels = data.y[data.test_mask].cpu().numpy()
        return {
            "auroc": roc_auc_score(labels, scores),
            "auprc": average_precision_score(labels, scores),
        }

    def extract_embeddings(self, data: Data) -> np.ndarray:
        data = data.to(self.device)
        self.model.eval()
        with torch.no_grad():
            emb = self.model.get_embeddings(data).cpu().numpy()
        return emb
