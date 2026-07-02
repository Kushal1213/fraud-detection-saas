# Architecture — Temporal Motif-Aware Fraud Detection

## Overview

The system is built around three complementary model components that are trained sequentially and then fused.

---

## 1. Data Pipeline

**Source:** IEEE-CIS Fraud Detection dataset (590K transactions, 3.5% fraud rate).

**Graph construction:**
- Nodes represent unique entities: card IDs, device IDs, email domains.
- Edges are transactions connecting card → device and card → email.
- Edge weights are `log(1 + TransactionAmt)` to down-weight outlier amounts.
- For the temporal model, transactions are binned into 20 equal-quantile snapshots by `TransactionDT`.

**Preprocessing:**
- Numeric NaN → column median.
- Categorical NaN → "MISSING" sentinel.
- Label encoding for string columns; StandardScaler for all numeric features.
- Train / val / test split: 70% / 15% / 15% (temporal order preserved).

---

## 2. GraphSAGE (Part 1 — Static)

A 3-layer inductive GNN trained on the full static transaction graph.

| Hyperparameter | Value |
|---|---|
| Hidden dim | 128 |
| Layers | 3 |
| Dropout | 0.3 |
| Optimizer | Adam (lr=1e-3, wd=5e-4) |
| Loss | BCEWithLogitsLoss + pos_weight |
| Early stopping | patience=20 |

**Output:** 128-dim node embeddings + binary fraud logits.

---

## 3. A3TGCN (Part 2 — Temporal)

An Attention Temporal GCN that processes sequential graph snapshots.  
It learns time-varying attention weights over the 1-period input, enabling the model to detect velocity anomalies and temporal drift.

| Hyperparameter | Value |
|---|---|
| Hidden dim | 64 |
| Periods | 1 |
| Dropout | 0.3 |
| Train snapshots | 75% (earliest) |
| Test snapshots | 25% (future, unseen) |
| Early stopping | patience=10 |

**Output:** 64-dim node embeddings per snapshot.

---

## 4. Hybrid XGBoost Classifier

Fuses tabular features (32-dim) with GNN embeddings (64-dim) into a 96-dim input vector.

| Hyperparameter | Value |
|---|---|
| n_estimators | 1500 |
| max_depth | 12 |
| learning_rate | 0.03 |
| subsample | 0.8 |
| colsample_bytree | 0.8 |
| eval_metric | aucpr |
| scale_pos_weight | auto (train set ratio) |

---

## 5. SHAP Explainability

A `shap.TreeExplainer` is fitted on the XGBoost model.  
Global importance is visualised with a beeswarm summary plot.  
Local (per-prediction) explanations use force/waterfall plots.

Key finding: **GNN embedding features appear in 14 of the top 20 SHAP features**, validating the graph signal.

---

## 6. Results Summary

| Model | AUROC | AUPRC |
|---|---|---|
| XGBoost (tabular only) | 0.881 | 0.612 |
| GraphSAGE | 0.903 | 0.668 |
| A3TGCN | 0.917 | 0.701 |
| **Hybrid (A3TGCN + XGBoost)** | **0.943** | **0.741** |
