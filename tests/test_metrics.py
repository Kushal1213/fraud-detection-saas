"""
test_metrics.py
---------------
Unit tests for src/utils/metrics.py
"""

import numpy as np
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from utils.metrics import auroc, auprc, precision_at_k, report


@pytest.fixture
def binary_data():
    rng = np.random.default_rng(42)
    y_true  = rng.integers(0, 2, size=200)
    y_score = np.clip(y_true + rng.normal(0, 0.3, size=200), 0, 1)
    return y_true, y_score


def test_auroc_range(binary_data):
    y_true, y_score = binary_data
    score = auroc(y_true, y_score)
    assert 0.5 <= score <= 1.0, f"AUROC out of expected range: {score}"


def test_auprc_range(binary_data):
    y_true, y_score = binary_data
    score = auprc(y_true, y_score)
    assert 0.0 < score <= 1.0, f"AUPRC out of range: {score}"


def test_precision_at_k(binary_data):
    y_true, y_score = binary_data
    p_at_k = precision_at_k(y_true, y_score, k=50)
    assert 0.0 <= p_at_k <= 1.0


def test_precision_at_k_perfect():
    y_true  = np.array([1, 1, 1, 0, 0])
    y_score = np.array([0.9, 0.8, 0.7, 0.3, 0.2])
    assert precision_at_k(y_true, y_score, k=3) == 1.0


def test_report_keys(binary_data):
    y_true, y_score = binary_data
    result = report(y_true, y_score)
    for key in ("auroc", "auprc", "precision_at_k", "precision", "recall", "f1"):
        assert key in result, f"Missing key: {key}"
