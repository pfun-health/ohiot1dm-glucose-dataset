---
layout: home
title: Home
nav_order: 1
---

# OhioT1DM Glucose Dataset

{: .fs-6 .fw-300 }
Blood-glucose forecasting and interpolation for Type 1 Diabetes —
comparing a data-driven **SimpleLSTM** with the physiological
**PFun CMA model**.

[Get started](getting-started){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
[View on GitHub](https://github.com/pfun-health/ohiot1dm-glucose-dataset){: .btn .fs-5 .mb-4 .mb-md-0 }

---

## What is this project?

This repository explores time-series forecasting and interpolation of continuous
glucose monitor (CGM) readings for patients with Type 1 Diabetes using the
[OhioT1DM dataset](https://doi.org/10.48550/arXiv.2109.02178) (12 patients,
2018 & 2020 cohorts).

Two modelling approaches are directly compared:

| Model | Type | Key strength |
|---|---|---|
| **SimpleLSTM** | Deep learning | Learns complex non-linear dynamics from multi-feature sequences |
| **PFun CMA** | Physiological / circadian | Interpretable parameters; fast inference; no training corpus needed |

---

## Key results (30-minute forecasting horizon)

| Metric | SimpleLSTM |
|---|---|
| RMSE | 17.66 ± 0.09 mg/dL |
| MAE | 15.93 ± 0.09 mg/dL |
| MARD | 0.106 ± 0.086 |

Full results including the CMA model comparison are in
[Notebook 02](notebooks/02-comparison).

---

## Highlights

- **Reproducible environment** — managed with [`uv`](https://docs.astral.sh/uv/)
  and a `flake.nix` Nix dev-shell.
- **Proper Python package** — `ohiot1dm_glucose_dataset` is installable with
  `uv sync` and exposes a clean public API.
- **Two Jupyter notebooks** — exploration + head-to-head model comparison with
  confusion matrices and regression metrics.
- **This documentation** — built with [Just the Docs](https://just-the-docs.com/)
  and deployed via GitHub Actions.
