---
layout: default
title: "02 — LSTM vs CMA Comparison"
parent: Notebooks
nav_order: 2
---

# Notebook 02 — LSTM vs PFun CMA Model Comparison
{: .no_toc }

**File:** `notebooks/02_comparison_lstm_vs_cma.ipynb`

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Overview

A head-to-head comparison of `SimpleLSTM` and the
[PFun CMA model](https://github.com/pfun-health/pfun-cma-model)
on two tasks:

| Task | Definition |
|---|---|
| **Interpolation** | Imputing glucose readings where `missing_cbg == 1` |
| **Forecasting** | Predicting the glucose value 30 minutes ahead |

---

## Models

### SimpleLSTM

Trained on the Ohio 2018 + 2020 train split using the same hyperparameters as
Notebook 01.  Forecasting is performed auto-regressively (`n_steps = 6` steps
of 5 min each).

### PFun CMA Model

The Cortisol–Melatonin–Adiponectin (CMA) model is a physiological
circadian model that fits a parameterised glucose curve to a 24-hour window.

Parameters optimised per patient file:

| Parameter | Meaning |
|---|---|
| `d` | Timezone / circadian offset (hours) |
| `taup` | Photoperiod length (circadian scale) |
| `taug` | Glucose response time constant |
| `B` | Glucose bias |
| `Cm` | Cortisol temporal sensitivity |
| `toff` | Solar-noon offset |

Fitting uses `scipy.optimize.minimize` (L-BFGS-B) via `pfun_cma_model.engine.fit.fit_model`.

---

## Metrics

### Regression metrics

| Metric | Formula | Interpretation |
|---|---|---|
| RMSE | √MSE | Overall prediction error (mg/dL) |
| MAE | mean\|y−ŷ\| | Robust to outliers |
| MARD | mean(\|y−ŷ\|/y) | Relative error (unit-free) |
| R² | 1 − SS_res/SS_tot | Variance explained |

### Glucose-zone confusion matrix

Glucose values are binned into three clinically meaningful zones:

| Zone | Range |
|---|---|
| Hypoglycemia | < 70 mg/dL |
| Euglycemia | 70–180 mg/dL |
| Hyperglycemia | > 180 mg/dL |

Each confusion matrix is **row-normalised** so that the diagonal shows
per-zone recall.

---

## Notebook sections

1. **Imports & configuration** — thresholds, hyperparameters, random seeds.
2. **Data loading** — CSV discovery and sanity check.
3. **LSTM training** — full training loop with LR schedule.
4. **CMA fitting** — per-patient file fit with residual logging.
5. **Collect predictions** — helper functions for both forecasting and interpolation.
6. **Regression metrics table** — RMSE / MAE / MARD / R² for all four scenarios.
7. **Bar chart** — side-by-side metric comparison.
8. **Confusion matrices** — 2 × 2 grid (model × task), row-normalised heatmaps.
9. **Zone accuracy summary** — overall + per-zone recall table.
10. **Scatter plots** — hexbin predicted vs true for forecasting.
11. **Sample trace** — CMA smooth curve + LSTM step-ahead on a single patient.
12. **Summary table** — qualitative model comparison.

---

## Key takeaways

- LSTM typically achieves **lower RMSE** for short-horizon forecasting due to
  its access to multi-feature sequences.
- CMA performs competitively (or better) for **missing-value interpolation**
  because it leverages a continuous physiological prior.
- CMA parameters provide an **interpretable patient signature** (circadian
  profile) unavailable from LSTM weights.
- Both models agree on zone classification for the majority *euglycemic* range;
  disagreements are concentrated at the clinical boundaries.
