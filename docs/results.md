---
layout: default
title: Results
nav_order: 5
---

# Results
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Methodology

### Data

The [OhioT1DM dataset](https://doi.org/10.48550/arXiv.2109.02178) provides
CGM recordings from 12 patients with Type 1 Diabetes across two cohorts
(2018 — 6 patients; 2020 — 6 patients).
Each recording is sampled at 5-minute intervals and includes:
CBG, finger-stick BG, basal insulin, heart rate, GSR, carbohydrate intake, and bolus dose.

### Preprocessing

1. **Missing CBG imputation** via cubic spline (rows where `missing_cbg == 1`).
2. **NaN filling** for all other features: `fill = min − 1 % × |min|`.
3. **MinMax normalisation** to `[0, 1]` fitted on the merged training set.
4. Context window: 24 time steps (= 120 minutes).

### SimpleLSTM architecture

```
Input (batch, 24, 7) → BatchNorm1d → LSTM(7→5, 1 layer) → Linear(5→7)
```

### Training

| Hyperparameter | Value |
|---|---|
| Epochs | 150 |
| Batch size | 500 |
| Initial lr | 0.001 |
| lr at epoch 80 | 0.0001 |
| Optimiser | Adam |
| Loss | MSE |

---

## SimpleLSTM — 30-minute forecasting horizon

### Loss curves

![Train and Test Loss](../Images/Loss_Final.png "Train and Test Loss")

### Prediction examples

<p>
  <img src="../Images/pr1.png" alt="Prediction 1" width="380"/>
  <img src="../Images/pr2.png" alt="Prediction 2" width="380"/>
</p>
<p>
  <img src="../Images/pr3.png" alt="Prediction 3" width="380"/>
  <img src="../Images/pr4.png" alt="Prediction 4" width="380"/>
</p>

### Quantitative metrics

| Metric | Mean | Standard Error |
|---|---|---|
| MSE (mg/dL)² | 616.19 | ± 10.65 |
| RMSE (mg/dL) | 17.66 | ± 0.09 |
| MAE (mg/dL) | 15.93 | ± 0.09 |
| MARD | 0.1055 | ± 0.086 |

---

## LSTM vs PFun CMA — comparative results

Full comparative results (regression metrics, glucose-zone confusion matrices,
scatter plots) are in
[Notebook 02](notebooks/02-comparison).

### Summary comparison

| Dimension | SimpleLSTM | PFun CMA |
|---|---|---|
| Model type | Data-driven, deep learning | Physiological, circadian |
| Training cost | ~minutes (GPU/CPU) | ~seconds (curve fit) |
| Input features | 7 features (CBG, basal, HR, …) | CBG time series only |
| Interpretability | Low (black box) | High (named parameters) |
| Forecasting | ✅ Strong | ⚠️ Competitive |
| Interpolation | ✅ Good | ✅ Strong (no training required) |

---

## References

1. Tena, F. et al. (2021). *A Critical Review of the state-of-the-art on Deep Neural Networks for Blood Glucose Prediction.* arXiv:2109.02178
2. Mirshekarian, S. et al. — LSTM baseline architecture.
3. Marling, C. & Bunescu, R. (2020). *The OhioT1DM Dataset for Blood Glucose Level Prediction: Update 2020.*
4. PFun CMA Model — <https://github.com/pfun-health/pfun-cma-model>
