# OhioT1DM Glucose Dataset — LSTM & CMA Model

> Blood-glucose forecasting and interpolation for Type 1 Diabetes using the
> [OhioT1DM dataset](https://doi.org/10.48550/arXiv.2109.02178), comparing a
> data-driven **SimpleLSTM** with the physiological
> **[PFun CMA model](https://github.com/pfun-health/pfun-cma-model)**.

[![GitHub Pages](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://pfun-health.github.io/ohiot1dm-glucose-dataset/)

---

## Project Overview

This repository contains:

| Path | Description |
|---|---|
| `ohiot1dm_glucose_dataset/` | Installable Python package — data loading, LSTM model, training loop |
| `notebooks/01_lstm_glucose_exploration.ipynb` | Original exploration notebook (data loading, LSTM training, predictions) |
| `notebooks/02_comparison_lstm_vs_cma.ipynb` | **New** — LSTM vs CMA comparison: confusion matrices, RMSE/MAE/MARD, scatter plots |
| `scripts/` | Utility scripts (CSV → Parquet, dataset conversion) |
| `docs/` | Jekyll documentation site (served via GitHub Pages) |
| `flake.nix` | Nix dev-shell |

---

## Quick Start

### Prerequisites

- [uv](https://docs.astral.sh/uv/) ≥ 0.5 (replaces pip + virtualenv)
- Python 3.12 (managed by `uv` or pinned in `.python-version`)

### Install

```bash
# Clone
git clone https://github.com/pfun-health/ohiot1dm-glucose-dataset.git
cd ohiot1dm-glucose-dataset

# Install runtime + dev dependencies (includes Jupyter)
uv sync --dev
```

### Data

Place the OhioT1DM processed CSVs under:

```
Ohio Data/
├── Ohio2018_processed/
│   ├── train/   *.csv
│   └── test/    *.csv
└── Ohio2020_processed/
    ├── train/   *.csv
    └── test/    *.csv
```

### Run the LSTM training script

```bash
uv run ohiot1dm-train
```

### Open a notebook

```bash
uv run jupyter lab notebooks/
```

### Nix dev-shell

```bash
nix develop
# then: uv sync --dev && uv run jupyter lab notebooks/
```

---

## Package API

```python
from ohiot1dm_glucose_dataset import (
    OhioT1DMDataset,   # PyTorch Dataset
    SimpleLSTM,        # LSTM model
    create_dataloader, # convenience DataLoader factory
    train,             # full training loop
    plot_losses,       # loss visualisation
)
```

---

## Results (SimpleLSTM — 30-minute horizon)

| Metric | Value |
|---|---|
| MSE | 616.19 ± 10.65 |
| RMSE | 17.66 ± 0.09 mg/dL |
| MAE | 15.93 ± 0.09 mg/dL |
| MARD | 0.106 ± 0.086 |

See `Report.md` and `notebooks/02_comparison_lstm_vs_cma.ipynb` for full details
and a comparison with the PFun CMA model.

---

## Repository Structure

```
ohiot1dm-glucose-dataset/
├── .python-version              # Python 3.12
├── flake.nix                    # Nix dev-shell
├── pyproject.toml               # uv / build config
├── uv.lock                      # locked dependency graph
├── PATCH-NOTES.md               # changelog
├── AGENTS-TODO.md               # agent task tracker
├── README.md
├── Report.md                    # LSTM results report
├── Images/                      # result figures
├── Ohio Data/                   # dataset (not committed)
├── notebooks/
│   ├── 01_lstm_glucose_exploration.ipynb
│   └── 02_comparison_lstm_vs_cma.ipynb
├── ohiot1dm_glucose_dataset/    # Python package
│   ├── __init__.py
│   ├── data_processor_loader.py
│   ├── lstm_model.py
│   ├── training_function.py
│   └── main.py
├── scripts/
│   ├── convert2parquet.sh
│   └── convert2pfun.py
└── docs/                        # Jekyll documentation site
```

---

## References

1. Tena, F. et al. (2021). *A Critical Review of the state-of-the-art on Deep Neural Networks for Blood Glucose Prediction.* arXiv:2109.02178
2. Marling, C. & Bunescu, R. (2020). *The OhioT1DM Dataset for Blood Glucose Level Prediction: Update 2020.*
3. PFun CMA Model — <https://github.com/pfun-health/pfun-cma-model>
