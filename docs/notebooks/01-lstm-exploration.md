---
layout: default
title: "01 — LSTM Exploration"
parent: Notebooks
nav_order: 1
---

# Notebook 01 — LSTM Glucose Exploration
{: .no_toc }

**File:** `notebooks/01_lstm_glucose_exploration.ipynb`

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Overview

This is the original project notebook, migrated from Google Colab.
It walks through the full workflow from raw CSV loading to LSTM predictions.

---

## Contents

### Data loading & preprocessing

- Mounts / extracts the `Ohio Data` zip archive.
- Merges the 2018 and 2020 cohort CSVs.
- **Missing CBG imputation:** cubic spline interpolation on the `cbg` column
  (consistent with Tena et al., arXiv:2109.02178).
- **NaN filling for other features:** replaced with `min − 1 % × |min|` so that
  scaled values are distinguishable from legitimate zero readings.
- **MinMax normalisation** to `[0, 1]`.

### Model architecture

`SimpleLSTM` — a single hidden LSTM layer with BatchNorm1d on the input,
followed by a linear output layer:

```
Input (batch, seq_len, 7)
  → BatchNorm1d(7)
  → LSTM(7 → 5, 1 layer)
  → Linear(5 → 7)
Output (batch, 7)
```

A `SimpleCNN` alternative is also defined in the notebook for reference.

### Training loop

- 150 epochs, batch size 500, initial lr = 0.001.
- Learning rate divided by 10 at epoch 80.
- Best model selected by minimum validation MSE.

### Prediction visualisation

Auto-regressive multi-step forecasting at 30 min / 60 min / 120 min horizons,
plotted with context + ground truth + prediction.

### Metrics

| Metric | Value |
|---|---|
| MSE | 616.19 ± 10.65 (mg/dL)² |
| RMSE | 17.66 ± 0.09 mg/dL |
| MAE | 15.93 ± 0.09 mg/dL |
| MARD | 0.106 ± 0.086 |

---

## References

- Tena, F. et al. (2021). arXiv:2109.02178
- Mirshekarian et al. — LSTM architecture baseline
