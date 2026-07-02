"""
train.py
--------
End-to-end training script for the Temporal Motif-Aware Fraud Detection System.

Usage:
    python scripts/train.py --config configs/config.yaml
    python scripts/train.py --model temporal --epochs 50
    python scripts/train.py --model hybrid --embeddings artifacts/embeddings.npy
""""

import argparse
import logging
import yaml
import torch
import numpy as np
from pathlib import Path

# Project imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.preprocessor import FraudDataPreprocessor
from src.data.temporal_dataset import build_temporal_dataset, split_temporal
from src.models.graphsage_model import FraudGraphSAGE, GraphSAGETrainer
from src.models.temporal_model import A3TGCNFraudModel, TemporalTrainer
from src.models.hybrid_classifier import HybridFraudDetector
from src.explainability.shap_explainer import FraudExplainer
from src.utils.visualization import plot_roc_pr, plot_confusion_matrix, plot_model_comparison

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def load_config(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def train_graphsage(config: dict, device: str):
    """Part 1: Train static GraphSAGE model."""
    logger.info("=" * 60)
    logger.info("PART 1: GraphSAGE Static Fraud Detection")
    logger.info("=" * 60)

    prep = FraudDataPreprocessor(config)
    data, df = prep.prepare(
        raw_dir=config["data"]["raw_dir"],
        max_rows=config["data"]["max_rows"]
    )

    model = FraudGraphSAGE(
        in_channels=data.x.shape[1],
        hidden_channels=config["graphsage"]["hidden_channels"],
        num_layers=config["graphsage"]["num_layers"],
        dropout=config["graphsage"]["dropout"],
    )

    trainer = GraphSAGETrainer(model, device, config)
    trainer.train(data, save_path=f"{config['artifacts']['dir']}/{config['artifacts']['graphsage_model']}")
    results = trainer.evaluate(data)
    logger.info(f"GraphSAGE Test — AUROC: {results['auroc']:.4f} | AUPRC: {results['auprc']:.4f}")

    embeddings = trainer.extract_embeddings(data)
    np.save(f"{config['artifacts']['dir']}/graphsage_embeddings.npy", embeddings)

    return results, embeddings, data, prep


def train_temporal(config: dict, device: str):
    """Part 2: Train A3TGCN temporal model and hybrid XGBoost."""
    logger.info("=" * 60)
    logger.info("PART 2: A3TGCN Temporal Fraud Detection")
    logger.info("=" * 60)

    dataset = build_temporal_dataset(
        path_txn=f"{config['data']['raw_dir']}/{config['data']['train_transaction']}",
        path_id=f"{config['data']['raw_dir']}/{config['data']['train_identity']}",
        n_snapshots=config["data"]["n_snapshots"],
        max_rows=config["data"]["max_rows"],
    )

    train_dataset, test_dataset = split_temporal(dataset, config["temporal"]["train_split"])

    node_features = dataset.features[0].shape[1]
    model = A3TGCNFraudModel(
        node_features=node_features,
        hidden_dim=config["temporal"]["hidden_dim"],
        periods=config["temporal"]["periods"],
        dropout=config["temporal"]["dropout"],
    )

    trainer = TemporalTrainer(model, device, config)
    trainer.train(train_dataset, save_path=f"{config['artifacts']['dir']}/{config['artifacts']['temporal_model']}")
    results = trainer.evaluate(test_dataset)
    logger.info(f"Temporal GNN Test — AUROC: {results['auroc']:.4f} | AUPRC: {results['auprc']:.4f}")

    embeddings = trainer.extract_embeddings(dataset, snapshot_idx=-1)
    np.save(f"{config['artifacts']['dir']}/{config['artifacts']['embeddings']}", embeddings)

    return results, embeddings, dataset


def train_hybrid(config: dict, embeddings: np.ndarray, tabular: np.ndarray, labels: np.ndarray):
    """Train hybrid XGBoost on GNN embeddings + tabular features."""
    logger.info("=" * 60)
    logger.info("HYBRID: XGBoost on GNN Embeddings + Tabular Features")
    logger.info("=" * 60)

    detector = HybridFraudDetector(config)
    X = detector.build_features(tabular, embeddings)

    split = int(0.8 * len(X))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = labels[:split], labels[split:]

    detector.fit(X_train, y_train, X_val=X_test, y_val=y_test)
    results = detector.evaluate(X_test, y_test)
    detector.save(f"{config['artifacts']['dir']}/{config['artifacts']['xgboost_model']}")

    return results, detector, X_test, y_test


def main():
    parser = argparse.ArgumentParser(description="Train Temporal Fraud Detection System")
    parser.add_argument("--config", default="configs/config.yaml")
    parser.add_argument("--model", choices=["graphsage", "temporal", "hybrid", "all"], default="all")
    parser.add_argument("--epochs", type=int, default=None)
    parser.add_argument("--embeddings", type=str, default=None, help="Path to precomputed embeddings")
    args = parser.parse_args()

    config = load_config(args.config)
    if args.epochs:
        config["temporal"]["epochs"] = args.epochs
        config["graphsage"]["epochs"] = args.epochs

    Path(config["artifacts"]["dir"]).mkdir(parents=True, exist_ok=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Device: {device}")

    all_results = {}

    if args.model in ("graphsage", "all"):
        gs_results, gs_embeddings, data, prep = train_graphsage(config, device)
        all_results["GraphSAGE"] = gs_results

    if args.model in ("temporal", "all"):
        temp_results, temp_embeddings, dataset = train_temporal(config, device)
        all_results["A3TGCN (Temporal)"] = temp_results

        tabular = dataset.features[-1]
        labels  = dataset.targets[-1]
        hybrid_results, detector, X_test, y_test = train_hybrid(config, temp_embeddings, tabular, labels)
        all_results["Hybrid (A3TGCN + XGBoost)"] = hybrid_results

    if args.model == "hybrid" and args.embeddings:
        embeddings = np.load(args.embeddings)
        logger.info("Hybrid training with precomputed embeddings requires tabular data — run full pipeline.")

    logger.info("\n" + "=" * 60)
    logger.info("FINAL MODEL COMPARISON")
    logger.info("=" * 60)
    for name, res in all_results.items():
        logger.info(f"{name:35s} AUROC={res['auroc']:.4f}  AUPRC={res['auprc']:.4f}")

    if len(all_results) > 1:
        plot_model_comparison(all_results, metric="auroc",
                              save_path=f"{config['artifacts']['dir']}/model_comparison.png")


if __name__ == "__main__":
    main()
