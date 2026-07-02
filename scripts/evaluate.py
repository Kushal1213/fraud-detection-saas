"""
evaluate.py
------------
Standalone evaluation script for trained model checkpoints.

Usage:
    python scripts/evaluate.py --checkpoint artifacts/temporal_best.pth --data data/raw/
    python scripts/evaluate.py --model xgboost --checkpoint artifacts/hybrid_xgb.ubj
"""

import argparse
import logging
import yaml
import torch
import numpy as np
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.preprocessor import FraudDataPreprocessor
from src.data.temporal_dataset import build_temporal_dataset, split_temporal
from src.models.graphsage_model import FraudGraphSAGE, GraphSAGETrainer
from src.models.temporal_model import A3TGCNFraudModel, TemporalTrainer
from src.models.hybrid_classifier import HybridFraudDetector
from src.utils.visualization import plot_roc_pr, plot_confusion_matrix

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def evaluate_graphsage(config, checkpoint, device):
    prep = FraudDataPreprocessor(config)
    data, _ = prep.prepare(config["data"]["raw_dir"], config["data"]["max_rows"])

    model = FraudGraphSAGE(
        in_channels=data.x.shape[1],
        hidden_channels=config["graphsage"]["hidden_channels"],
        num_layers=config["graphsage"]["num_layers"],
        dropout=config["graphsage"]["dropout"],
    )
    model.load_state_dict(torch.load(checkpoint, map_location=device))

    trainer = GraphSAGETrainer(model, device, config)
    results = trainer.evaluate(data)
    logger.info(f"GraphSAGE  AUROC={results['auroc']:.4f}  AUPRC={results['auprc']:.4f}")
    return results


def evaluate_hybrid(config, checkpoint):
    detector = HybridFraudDetector.load(checkpoint, config)

    dataset = build_temporal_dataset(
        path_txn=f"{config['data']['raw_dir']}/{config['data']['train_transaction']}",
        path_id=f"{config['data']['raw_dir']}/{config['data']['train_identity']}",
        n_snapshots=config["data"]["n_snapshots"],
        max_rows=config["data"]["max_rows"],
    )
    tabular = dataset.features[-1]
    labels  = dataset.targets[-1]

    emb_path = f"{config['artifacts']['dir']}/{config['artifacts']['embeddings']}"
    embeddings = np.load(emb_path)

    X = detector.build_features(tabular, embeddings)
    results = detector.evaluate(X, labels)
    logger.info(f"Hybrid  AUROC={results['auroc']:.4f}  F1={results['f1']:.4f}")
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config",     default="configs/config.yaml")
    parser.add_argument("--model",      choices=["graphsage", "xgboost"], default="graphsage")
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--data",       default=None)
    args = parser.parse_args()

    with open(args.config) as f:
        config = yaml.safe_load(f)
    if args.data:
        config["data"]["raw_dir"] = args.data

    device = "cuda" if torch.cuda.is_available() else "cpu"

    if args.model == "graphsage":
        evaluate_graphsage(config, args.checkpoint, device)
    else:
        evaluate_hybrid(config, args.checkpoint)


if __name__ == "__main__":
    main()
