"""
test_models.py
--------------
Unit tests for GraphSAGE, A3TGCN, and HybridFraudDetector.
Runs on CPU with tiny synthetic data — no GPU or real dataset required.
"""

import numpy as np
import torch
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from models.graphsage_model import FraudGraphSAGE
from models.temporal_model import A3TGCNFraudModel


# -----------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------

@pytest.fixture
def tiny_graph():
    """10-node synthetic graph."""
    from torch_geometric.data import Data
    x = torch.randn(10, 8)
    edge_index = torch.tensor([[0,1,2,3,4],[1,2,3,4,0]], dtype=torch.long)
    y = torch.randint(0, 2, (10,)).float()
    mask = torch.zeros(10, dtype=torch.bool)
    mask[:8] = True
    return Data(x=x, edge_index=edge_index, y=y,
                train_mask=mask, val_mask=~mask, test_mask=~mask)


@pytest.fixture
def sage_model(tiny_graph):
    return FraudGraphSAGE(in_channels=8, hidden_channels=16, num_layers=2)


# -----------------------------------------------------------------------
# GraphSAGE tests
# -----------------------------------------------------------------------

def test_sage_forward_shape(sage_model, tiny_graph):
    out = sage_model(tiny_graph)
    assert out.shape == (10,), f"Expected (10,), got {out.shape}"


def test_sage_embeddings_shape(sage_model, tiny_graph):
    emb = sage_model.get_embeddings(tiny_graph)
    assert emb.shape == (10, 16)


def test_sage_training_step(sage_model, tiny_graph):
    optimizer = torch.optim.Adam(sage_model.parameters(), lr=1e-3)
    criterion = torch.nn.BCEWithLogitsLoss()
    sage_model.train()
    out  = sage_model(tiny_graph)
    loss = criterion(out[tiny_graph.train_mask],
                     tiny_graph.y[tiny_graph.train_mask])
    loss.backward()
    optimizer.step()
    assert loss.item() > 0


# -----------------------------------------------------------------------
# A3TGCN tests
# -----------------------------------------------------------------------

def test_a3tgcn_forward_shape():
    model = A3TGCNFraudModel(node_features=4, hidden_dim=8, periods=1)
    x = torch.randn(5, 4, 1)           # (nodes, features, periods)
    edge_index = torch.tensor([[0,1,2],[1,2,0]], dtype=torch.long)
    logits, emb = model(x, edge_index)
    assert logits.shape == (5,)
    assert emb.shape    == (5, 8)


def test_a3tgcn_embeddings_shape():
    model = A3TGCNFraudModel(node_features=4, hidden_dim=8, periods=1)
    x = torch.randn(5, 4, 1)
    edge_index = torch.tensor([[0,1],[1,0]], dtype=torch.long)
    emb = model.get_embeddings(x, edge_index)
    assert emb.shape == (5, 8)
