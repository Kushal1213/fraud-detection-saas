"""
temporal_dataset.py
-------------------
Builds a DynamicGraphTemporalSignal from the IEEE-CIS dataset,
splitting transactions into equal-quantile time snapshots.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from torch_geometric_temporal.signal import DynamicGraphTemporalSignal
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

CATEGORICAL_COLS = ["ProductCD", "card4", "card6", "P_emaildomain",
                    "R_emaildomain", "DeviceType", "DeviceInfo"]


def _load_and_preprocess(path_txn: str, path_id: str = None,
                          max_rows: int = None) -> pd.DataFrame:
    df = pd.read_csv(path_txn, nrows=max_rows)
    if path_id:
        try:
            idf = pd.read_csv(path_id, nrows=max_rows)
            df = df.merge(idf, on="TransactionID", how="left")
        except FileNotFoundError:
            logger.warning("Identity file not found.")

    # Impute
    for col in df.select_dtypes(include="number").columns:
        df[col] = df[col].fillna(df[col].median())
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].fillna("MISSING")

    # Encode categoricals
    le = LabelEncoder()
    for col in CATEGORICAL_COLS:
        if col in df.columns:
            df[col] = le.fit_transform(df[col].astype(str))

    # Sort by time
    df = df.sort_values("TransactionDT").reset_index(drop=True)
    return df


def build_temporal_dataset(path_txn: str, path_id: str = None,
                            n_snapshots: int = 20,
                            max_rows: int = None) -> DynamicGraphTemporalSignal:
    """
    Splits transactions into `n_snapshots` equal-quantile time bins and
    returns a DynamicGraphTemporalSignal object.

    Each snapshot contains:
    - feature matrix  : (num_nodes, num_features)
    - edge_index      : (2, num_edges) — card-group co-occurrence edges
    - edge_weight     : (num_edges,)   — log(1 + TransactionAmt)
    - targets         : (num_nodes,)   — isFraud labels
    """
    df = _load_and_preprocess(path_txn, path_id, max_rows)

    drop_cols = {"TransactionID", "isFraud", "TransactionDT"}
    feat_cols = [c for c in df.select_dtypes(include="number").columns
                 if c not in drop_cols]

    scaler = StandardScaler()
    X_all  = scaler.fit_transform(df[feat_cols].values)
    y_all  = df["isFraud"].values

    bins = pd.qcut(df["TransactionDT"], q=n_snapshots, labels=False,
                   duplicates="drop")
    unique_bins = sorted(bins.unique())

    edge_indices, edge_weights, features, targets = [], [], [], []

    for b in unique_bins:
        mask = (bins == b).values
        sub  = df[mask]
        X_b  = X_all[mask]
        y_b  = y_all[mask]

        # Build edges within snapshot via card1 grouping
        src, dst, ew = [], [], []
        if "card1" in sub.columns:
            local_idx = {orig: local for local, orig in enumerate(sub.index)}
            for idxs in sub.groupby("card1").groups.values():
                idxs = [local_idx[i] for i in idxs if i in local_idx]
                for i in range(len(idxs) - 1):
                    amt = float(sub.iloc[idxs[i]].get("TransactionAmt", 1))
                    src.append(idxs[i]);     dst.append(idxs[i + 1])
                    ew.append(np.log1p(amt))
                    src.append(idxs[i + 1]); dst.append(idxs[i])
                    ew.append(np.log1p(amt))

        if not src:
            n = len(sub)
            src = list(range(n)); dst = list(range(n)); ew = [1.0] * n

        edge_indices.append(np.array([src, dst], dtype=np.int64))
        edge_weights.append(np.array(ew, dtype=np.float32))
        features.append(X_b.astype(np.float32))
        targets.append(y_b.astype(np.float32))

    logger.info(f"Built {len(unique_bins)} temporal snapshots")
    return DynamicGraphTemporalSignal(edge_indices, edge_weights, features, targets)


def split_temporal(dataset: DynamicGraphTemporalSignal,
                   train_ratio: float = 0.75):
    """Split a DynamicGraphTemporalSignal into train / test by time."""
    n = dataset.snapshot_count
    split = int(train_ratio * n)

    train = DynamicGraphTemporalSignal(
        dataset.edge_indices[:split],
        dataset.edge_weights[:split],
        dataset.features[:split],
        dataset.targets[:split],
    )
    test = DynamicGraphTemporalSignal(
        dataset.edge_indices[split:],
        dataset.edge_weights[split:],
        dataset.features[split:],
        dataset.targets[split:],
    )
    logger.info(f"Temporal split: {split} train / {n - split} test snapshots")
    return train, test
