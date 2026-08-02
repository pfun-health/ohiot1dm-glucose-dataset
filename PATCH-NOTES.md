# Patch Notes

All notable changes to this project are documented here.
Format is inspired by [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased] — 2026-08-02

### Added
- `notebooks/` directory to hold all Jupyter notebooks.
- `notebooks/01_lstm_glucose_exploration.ipynb` — the original Colab notebook,
  moved here from the repository root and renamed for clarity.
- `notebooks/02_comparison_lstm_vs_cma.ipynb` — new notebook comparing
  `SimpleLSTM` and the PFun CMA model across:
  - Glucose interpolation (imputing `missing_cbg == 1` entries).
  - 30-minute blood-glucose forecasting.
  - Regression metrics: RMSE, MAE, MARD, R².
  - Row-normalised glucose-zone confusion matrices
    (Hypoglycemia / Euglycemia / Hyperglycemia).
  - Side-by-side scatter and bar-chart visualisations.
- `flake.nix` — Nix dev-shell with Python 3.12, `uv`, and required system libs.
- `PATCH-NOTES.md` — this file.
- `AGENTS-TODO.md` — agent-maintained task list.

### Changed
- `pyproject.toml`:
  - Description updated to reflect the project scope.
  - `requires-python` tightened to `>=3.12,<3.13` (matches `.python-version`).
  - Added `numpy>=1.24.0` and `scipy>=1.11.3` as explicit runtime dependencies.
  - Added `seaborn` as a runtime dependency (used by comparison notebook).
  - Dev group expanded: `ipykernel`, `jupyter`, `nbformat`, `seaborn`.
  - Added `[tool.uv.sources]` pointing `pfun-cma-model` at its GitHub repo.
  - Added `[project.scripts]` entry-point `ohiot1dm-train`.
  - Added `[build-system]` (hatchling) and `[tool.hatch.build.targets.wheel]`.
- Python source files relocated into the `ohiot1dm_glucose_dataset` package:
  - `data_processor_loader.py` → `ohiot1dm_glucose_dataset/data_processor_loader.py`
  - `lstm_model.py`            → `ohiot1dm_glucose_dataset/lstm_model.py`
  - `training_function.py`     → `ohiot1dm_glucose_dataset/training_function.py`
  - `main.py`                  → `ohiot1dm_glucose_dataset/main.py`
- All intra-package `import` statements updated to use absolute package paths
  (`from ohiot1dm_glucose_dataset.X import Y`).
- Hard-coded `os.getcwd()` path references replaced with
  `Path(__file__).parents[N]`-based resolution so the package works when
  installed or invoked from any working directory.
- `ohiot1dm_glucose_dataset/__init__.py` — now exports the public API
  (`OhioT1DMDataset`, `SimpleLSTM`, `create_dataloader`, `train`, …).
- `scripts/convert2pfun.py` — import updated to use the package namespace.
- `training_function.py` — fixed a bug where `lstm_model.state_dict()` was
  called on an undefined name; replaced with `model.state_dict()`.

### Removed
- `Gluc_proj_env.yaml` — superseded by `pyproject.toml` / `uv.lock`.
- `Glucese_proj_notebook.ipynb` (root) — moved to
  `notebooks/01_lstm_glucose_exploration.ipynb`.
