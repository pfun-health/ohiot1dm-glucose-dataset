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

## PFun CMA compatibility

`ohiot1dm_glucose_dataset` includes a bridge to the
[`pfun-cma-model`](https://github.com/pfun-health/pfun-cma-model) package for
fitting the physiological CMA model to OhioT1DM CSVs. pfun is an optional
*dev* dependency — install it with `uv sync --dev`. The package itself
imports without it, and any function that needs pfun raises a helpful
`ImportError` when it is missing.

### Command-line interface

`scripts/convert2pfun.py` converts CSVs to pfun format and fits the CMA model:

```bash
# List the patient test CSVs under Ohio Data/*/test/
uv run python scripts/convert2pfun.py --list

# Convert CSVs to pfun format (writes {stem}_pfun.csv into converted/)
uv run python scripts/convert2pfun.py --convert \
    "Ohio Data/Ohio2018_processed/test/559-ws-testing_processed.csv"

# Fit CMA to every test CSV and print residual + fitted parameters
uv run python scripts/convert2pfun.py --fit

# Fit, then print regression metrics + glucose-zone confusion matrix
uv run python scripts/convert2pfun.py --fit --metrics --N 288 --n-steps 6
```

| Flag | Description |
|---|---|
| `--list` | List patient test CSVs |
| `--convert [PATH ...]` | Write pfun-format CSVs to `--outdir` (default `converted/`) |
| `--fit [PATH ...]` | Fit CMA per file; print residual + parameters |
| `--metrics` | Print regression metrics + zone confusion matrix (requires `--fit`) |
| `--N` | Model output samples, a positive integer (default `288`) |
| `--units` | `mgdl` only (default `mgdl`) |
| `--format` | `text` or `json` metrics output (default `text`) |
| `--n-steps` | Forecast horizon in model-grid steps, a positive integer (default `6`) |
| `--outdir` | Output directory for `--convert`, created as needed (default `converted`) |

Positional `PATH` arguments (files or directories) are merged with the
`--convert` / `--fit` values; with none supplied, all test CSVs under
`Ohio Data/*/test/` are used. The script creates a `logs/` directory in the
current working directory, which pfun requires for its log file.

`--convert` is resilient: a bad file is reported with a `FAILED:` line and
skipped, so one broken CSV does not abort the batch. The run ends with a
`Wrote k of n file(s).` summary line followed by the paths written.

### Package functions

```python
from ohiot1dm_glucose_dataset import (
    load_ohio_csv,
    convert_ohio_to_pfun,
    fit_patient,
    fit_patients,
    unscale_glucose,
    collect_predictions,
    regression_metrics,
    glucose_zone,
    zone_metrics,
)

fpath = "Ohio Data/Ohio2018_processed/test/559-ws-testing_processed.csv"

df = load_ohio_csv(fpath)                          # attach time + sg/value columns
formatted = convert_ohio_to_pfun(fpath)            # pfun format_data output
results = fit_patients(["Ohio Data/Ohio2018_processed/test/"])  # fit CMA per file

y_true, y_pred = collect_predictions(results, n_steps=6)  # normalized [0, 2]
metrics = regression_metrics(
    unscale_glucose(y_true),
    unscale_glucose(y_pred),
)
```

Full API reference: [PFun CMA Compatibility](api/pfun-utils).

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
