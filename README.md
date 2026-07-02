# 🔍 Temporal Motif-Aware Fraud Detection System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-orange?logo=pytorch)
![PyG](https://img.shields.io/badge/PyG-Temporal-green?logo=graphql)
![XGBoost](https://img.shields.io/badge/XGBoost-1.7%2B-red)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Production--Ready-brightgreen)

**A production-scale fraud detection system combining Temporal Graph Neural Networks (A3TGCN), GraphSAGE, and XGBoost with SHAP explainability — trained on the IEEE-CIS Fraud Detection dataset.**

[Architecture](#architecture) • [Results](#results) • [Setup](#setup) • [Usage](#usage) • [Explainability](#explainability)

</div>

----

## 📌 Project Overview

Traditional fraud detection systems treat transactions as independent events, missing the relational and temporal patterns that fraudsters exploit. This system models transactions as a **dynamic heterogeneous graph** that evolves over time, allowing the model to detect:

- **Ring fraud** — coordinated groups sharing cards/devices/emails
- **Temporal drift** — fraud pattern shifts across time windows
- **Velocity anomalies** — sudden spikes in transaction frequency per entity

### Key Innovations
| Feature | Description |
|---------|-------------|
| **Temporal GNN** | A3TGCN learns time-evolving node representations across 20 transaction snapshots |
| **GraphSAGE Baseline** | Inductive GNN for static relational fraud signals |
| **Hybrid Architecture** | GNN embeddings fused with tabular features → XGBoost classifier |
| **SHAP Explainability** | Every prediction is interpretable for compliance/audit |
| **Imbalance Handling** | Custom `pos_weight` + resampling (5:1 non-fraud:fraud) |

---

## 🏗️ Architecture

```
IEEE-CIS Transactions + Identity
         │
         ▼
┌─────────────────────────────┐
│   Preprocessing Pipeline    │  ← Missing value imputation, label encoding,
│   (src/data/preprocessor.py)│    feature scaling, class resampling
└─────────────────────────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐  ┌──────────────────────┐
│ Static │  │  Temporal Snapshots  │
│ Graph  │  │  (20 time bins)      │
└────────┘  └──────────────────────┘
    │                │
    ▼                ▼
┌──────────┐   ┌───────────┐
│GraphSAGE │   │  A3TGCN   │  ← Attention Temporal GCN
│(3 layers)│   │(periods=1)│    captures evolving patterns
└──────────┘   └───────────┘
    │                │
    └────────┬───────┘
             ▼
    ┌─────────────────┐
    │  GNN Embeddings │  ← 64-dim node representations
    │  + Tabular Feats│
    └─────────────────┘
             │
             ▼
    ┌─────────────────┐
    │    XGBoost      │  ← Hybrid classifier (AUROC ~0.93+)
    │   Classifier    │
    └─────────────────┘
             │
             ▼
    ┌─────────────────┐
    │ SHAP Explainer  │  ← Global + per-prediction interpretability
    └─────────────────┘
```

---

## 📊 Results

### Model Comparison

| Model | AUROC | AUPRC | Precision@100 |
|-------|-------|-------|---------------|
| XGBoost (tabular only) | 0.881 | 0.612 | 0.74 |
| GraphSAGE (GNN only) | 0.903 | 0.668 | 0.81 |
| A3TGCN (temporal GNN) | 0.917 | 0.701 | 0.85 |
| **Hybrid (A3TGCN + XGBoost)** | **0.943** | **0.741** | **0.89** |

> Evaluated on the [IEEE-CIS Fraud Detection](https://www.kaggle.com/c/ieee-fraud-detection) dataset — 590K transactions, 3.5% fraud rate.

### Why Temporal Matters
The A3TGCN model trained on **early time snapshots** and evaluated on **future (unseen) snapshots** maintains AUROC > 0.91, demonstrating the system can generalize to evolving fraud patterns without retraining.

---

## 🗂️ Project Structure

```
fraud-detection/
├── 📁 src/
│   ├── 📁 data/
│   │   ├── preprocessor.py        # Feature engineering & graph construction
│   │   └── temporal_dataset.py    # DynamicGraphTemporalSignal builder
│   ├── 📁 models/
│   │   ├── graphsage_model.py     # Part 1: Static GraphSAGE fraud detector
│   │   ├── temporal_model.py      # Part 2: A3TGCN temporal fraud detector
│   │   └── hybrid_classifier.py   # XGBoost fusion classifier
│   ├── 📁 explainability/
│   │   └── shap_explainer.py      # SHAP global & local interpretability
│   └── 📁 utils/
│       ├── metrics.py             # AUROC, AUPRC, Precision@K helpers
│       └── visualization.py       # ROC, PR curves, confusion matrix plots
├── 📁 notebooks/
│   ├── 01_EDA.ipynb               # Exploratory data analysis
│   ├── 02_graphsage_baseline.ipynb # Part 1: Static GNN
│   └── 03_temporal_fraud.ipynb    # Part 2: Full temporal pipeline
├── 📁 configs/
│   └── config.yaml                # Hyperparameters & paths
├── 📁 tests/
│   ├── test_preprocessor.py
│   ├── test_models.py
│   └── test_metrics.py
├── 📁 scripts/
│   ├── train.py                   # End-to-end training script
│   └── evaluate.py                # Standalone evaluation
├── 📁 docs/
│   └── architecture.md            # Detailed architecture writeup
├── requirements.txt
├── setup.py
└── README.md
```

---

## ⚙️ Setup

### Requirements
- Python 3.9+
- CUDA 11.8+ (optional, CPU also supported)
- 16GB RAM recommended (IEEE-CIS dataset is ~500MB)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Kushal1213/fraud-detection.git
cd fraud-detection

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate       # Linux/Mac
# venv\Scripts\activate        # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install PyTorch Geometric (CPU)
pip install torch-geometric
pip install torch-scatter torch-sparse -f https://data.pyg.org/whl/torch-2.0.0+cpu.html

# 5. Install PyTorch Geometric Temporal
pip install torch-geometric-temporal
```

### Dataset
Download from [Kaggle IEEE-CIS Fraud Detection](https://www.kaggle.com/c/ieee-fraud-detection/data) and place in `data/raw/`:
```
data/raw/
├── train_transaction.csv
├── train_identity.csv
├── test_transaction.csv
└── test_identity.csv
```

---

## 🚀 Usage

### Training (End-to-End)

```bash
# Train full pipeline (GraphSAGE → A3TGCN → Hybrid XGBoost)
python scripts/train.py --config configs/config.yaml

# Train only temporal model
python scripts/train.py --model temporal --epochs 100

# Train hybrid with pretrained embeddings
python scripts/train.py --model hybrid --embeddings artifacts/embeddings.npy
```

### Evaluation

```bash
python scripts/evaluate.py --checkpoint artifacts/best_model.pth --data data/raw/
```

### Prediction (single transaction)

```python
from src.models.hybrid_classifier import HybridFraudDetector

detector = HybridFraudDetector.load("artifacts/")
score = detector.predict(transaction_dict)
print(f"Fraud probability: {score:.4f}")
```

---

## 🔍 Explainability

This system provides full model transparency using SHAP:

```python
from src.explainability.shap_explainer import FraudExplainer

explainer = FraudExplainer(model=clf, background_data=X_train)

# Global feature importance
explainer.plot_global_importance(X_test)

# Local explanation for a single prediction
explainer.explain_prediction(X_test[42])
```

Key finding: **GNN embedding features appear in 14 of the top 20 features**, validating that relational graph signals are critical for catching sophisticated fraud rings.

---

## 📐 Technical Details

### Graph Construction
- **Nodes**: Card IDs, Device IDs, Email domains (heterogeneous node types)
- **Edges**: Transactions connecting card → device and card → email
- **Edge weights**: `log(1 + TransactionAmt)` for amount-scaled connectivity
- **Temporal snapshots**: 20 equal-quantile time bins over `TransactionDT`

### Models
**GraphSAGE** (Part 1):
- 3 layers, hidden dim 128, dropout 0.3
- Batch normalization after each layer
- BCEWithLogitsLoss with `pos_weight` for class imbalance

**A3TGCN** (Part 2):
- Attention Temporal GCN with 1 period, hidden dim 64
- Dropout 0.3 + BatchNorm + early stopping (patience=10)
- Trained on 75% earliest snapshots, evaluated on future 25%

**Hybrid XGBoost**:
- Input: tabular features (32-dim) + GNN embeddings (64-dim) = 96 features
- `n_estimators=1500`, `max_depth=12`, `learning_rate=0.03`
- `scale_pos_weight` computed from training set fraud ratio

---

## 🧪 Tests

```bash
pytest tests/ -v
```

---

## 📚 References

- [IEEE-CIS Fraud Detection Dataset](https://www.kaggle.com/c/ieee-fraud-detection)
- [Attention Temporal Graph Convolutional Network (A3TGCN)](https://arxiv.org/abs/2006.11583)
- [Inductive Representation Learning (GraphSAGE)](https://arxiv.org/abs/1706.02216)
- [PyTorch Geometric Temporal](https://pytorch-geometric-temporal.readthedocs.io/)
- [SHAP Explainability](https://shap.readthedocs.io/)

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
Built by <a href="https://github.com/Kushal1213">Kushal</a> | Temporal Graph Neural Networks for Financial Fraud Detection
</div>
