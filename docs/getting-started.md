---
layout: default
title: Getting Started
nav_order: 2
---

# Getting Started
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Prerequisites

| Tool | Version | Notes |
|---|---|---|
| Python | 3.12 | Pinned in `.python-version` |
| [uv](https://docs.astral.sh/uv/) | ≥ 0.5 | Replaces pip + virtualenv |
| Nix (optional) | any | For the `flake.nix` dev-shell |

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/pfun-health/ohiot1dm-glucose-dataset.git
cd ohiot1dm-glucose-dataset
```

### 2. Install dependencies

```bash
# Install runtime + dev dependencies (Jupyter, ipykernel, seaborn …)
uv sync --dev
```

> **Note:** `pfun-cma-model` is sourced directly from GitHub.
> The first `uv sync` will clone and build it — this may take a minute.

### 3. (Optional) Nix dev-shell

```bash
nix develop
# The shell hook prints usage instructions and sets UV_PYTHON automatically.
uv sync --dev
```

---

## Data setup

The OhioT1DM dataset is **not included** in this repository.
Place the pre-processed CSV files under:

```
Ohio Data/
├── Ohio2018_processed/
│   ├── train/
│   │   └── *.csv
│   └── test/
│       └── *.csv
└── Ohio2020_processed/
    ├── train/
    │   └── *.csv
    └── test/
        └── *.csv
```

Each CSV has the following columns:

| Column | Description |
|---|---|
| `5minute_intervals_timestamp` | Sequential 5-minute counter |
| `missing_cbg` | 1 = CBG reading was missing |
| `cbg` | Continuous blood glucose (mg/dL) |
| `finger` | Finger-stick BG reading |
| `basal` | Basal insulin rate |
| `hr` | Heart rate |
| `gsr` | Galvanic skin response |
| `carbInput` | Carbohydrate estimate (g) |
| `bolus` | Bolus insulin dose |

---

## Running the LSTM training script

```bash
uv run ohiot1dm-train
```

This trains a `SimpleLSTM` (hidden size 5, 1 layer, 150 epochs) on all
available training CSVs, saves `best_model.pth` and `simple_lstm_model.pth`,
and displays training / test loss curves.

---

## Opening a notebook

```bash
uv run jupyter lab notebooks/
```

| Notebook | Description |
|---|---|
| `01_lstm_glucose_exploration.ipynb` | Data loading, preprocessing, LSTM training, predictions |
| `02_comparison_lstm_vs_cma.ipynb` | LSTM vs CMA: confusion matrices, regression metrics, scatter plots |

---

## Package import

```python
from ohiot1dm_glucose_dataset import (
    OhioT1DMDataset,    # torch.utils.data.Dataset
    SimpleLSTM,         # nn.Module
    create_dataloader,  # convenience factory
    train,              # training loop
    plot_losses,        # loss visualisation
)
```
