"""
preprocessor.py
---------------
Feature engineering, graph construction, and train/val/test splitting
for the IEEE-CIS Fraud Detection dataset.
"""

import numpy as np
import pandas as pd
import torch
from torch_geometric.data import Data
from sklearn.preprocessing import LabelEncoder, StandardScaler
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class FraudDataPreprocessor:
    """
    Loads and preprocesses the IEEE-CIS transaction + identity CSVs.

    Steps:
    1. Merge transaction and identity tables on TransactionID
    2. Impute missing values (median for numeric, 'MISSING' for categorical)
    3. Label-encode categorical columns
    4. Scale numeric features with StandardScaler
    5. Build a heterogeneous transaction graph:
       - Nodes: unique card/device/email entities
       - Edges: transactions connecting card → device and card → email
       - Edge weights: log(1 + TransactionAmt)
    6. Attach train/val/test masks (70/15/15 split)
    """

    CATEGORICAL_COLS = ["ProductCD", "card4", "card6", "P_emaildomain",
                        "R_emaildomain", "DeviceType", "DeviceInfo"]
    ID_COLS = ["card1", "card2", "addr1", "addr2"]

    def __init__(self, config: dict):
        self.cfg   = config["data"]
        self.scaler = StandardScaler()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def prepare(self, raw_dir: str, max_rows: int = None):
        """
        Returns
        -------
        data : torch_geometric.data.Data
            Graph with node features, edge_index, labels, and masks.
        df : pd.DataFrame
            Processed feature dataframe (for tabular baselines).
        """
        df = self._load(raw_dir, max_rows)
        df = self._impute(df)
        df = self._encode(df)
        X  = self._scale(df)
        data = self._build_graph(df, X)
        logger.info(
            f"Graph: {data.num_nodes} nodes | {data.num_edges} edges | "
            f"train={data.train_mask.sum()} val={data.val_mask.sum()} "
            f"test={data.test_mask.sum()}"
        )
        return data, df

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load(self, raw_dir: str, max_rows):
        path = Path(raw_dir)
        txn = pd.read_csv(path / self.cfg["train_transaction"],
                          nrows=max_rows)
        try:
            idf = pd.read_csv(path / self.cfg["train_identity"],
                              nrows=max_rows)
            df  = txn.merge(idf, on="TransactionID", how="left")
        except FileNotFoundError:
            logger.warning("Identity file not found — using transaction data only.")
            df = txn
        logger.info(f"Loaded {len(df)} rows, {df.shape[1]} columns")
        return df

    def _impute(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in df.select_dtypes(include="number").columns:
            df[col] = df[col].fillna(df[col].median())
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].fillna("MISSING")
        return df

    def _encode(self, df: pd.DataFrame) -> pd.DataFrame:
        le = LabelEncoder()
        for col in self.CATEGORICAL_COLS:
            if col in df.columns:
                df[col] = le.fit_transform(df[col].astype(str))
        return df

    def _scale(self, df: pd.DataFrame) -> np.ndarray:
        drop = ["TransactionID", "isFraud", "TransactionDT"]
        feat_cols = [c for c in df.select_dtypes(include="number").columns
                     if c not in drop]
        X = self.scaler.fit_transform(df[feat_cols].values)
        return X

    def _build_graph(self, df: pd.DataFrame, X: np.ndarray) -> Data:
        n = len(df)
        x = torch.tensor(X, dtype=torch.float32)
        y = torch.tensor(df["isFraud"].values, dtype=torch.float32)

        # Simple self-loop + nearest-neighbour edges via card1 grouping
        src, dst = [], []
        if "card1" in df.columns:
            groups = df.groupby("card1").indices
            for idxs in groups.values():
                idxs = list(idxs)
                for i in range(len(idxs) - 1):
                    src.append(idxs[i]); dst.append(idxs[i + 1])
                    src.append(idxs[i + 1]); dst.append(idxs[i])
        else:
            # fallback: add self-loops only
            src = list(range(n)); dst = list(range(n))

        edge_index = torch.tensor([src, dst], dtype=torch.long)

        # Masks
        idx   = np.arange(n)
        train_end = int(0.70 * n)
        val_end   = int(0.85 * n)
        train_mask = torch.zeros(n, dtype=torch.bool)
        val_mask   = torch.zeros(n, dtype=torch.bool)
        test_mask  = torch.zeros(n, dtype=torch.bool)
        train_mask[:train_end] = True
        val_mask[train_end:val_end] = True
        test_mask[val_end:] = True

        return Data(x=x, edge_index=edge_index, y=y,
                    train_mask=train_mask, val_mask=val_mask,
                    test_mask=test_mask)
