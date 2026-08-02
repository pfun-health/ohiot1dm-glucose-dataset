# Patch Notes

All notable changes to this project are documented here.
Format is inspired by [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased] — 2026-08-02 (second pass)

### Added
- **Jekyll documentation site** (`docs/`) built with the
  [Just the Docs](https://just-the-docs.com/) theme:
  - `docs/_config.yml` — site metadata, theme config, GitHub source links.
  - `docs/Gemfile` — `jekyll ~> 4.3` + `just-the-docs ~> 0.10`.
  - `docs/index.md` — landing page with project summary and key results.
  - `docs/getting-started.md` — installation, data setup, usage examples.
  - `docs/notebooks/` — per-notebook documentation pages.
  - `docs/api/` — hand-written API reference for all public symbols.
  - `docs/results.md` — loss curves, prediction examples, metric tables.
  - `docs/development.md` — project layout, dependencies, Nix shell, CI.
- `.github/workflows/pages.yml` — GitHub Actions workflow to build and deploy
  the Jekyll site to GitHub Pages on every push to `main`.

### Changed
- `ohiot1dm_glucose_dataset/data_processor_loader.py` — comprehensive cleanup:
  - Removed duplicate `from pathlib import Path` import.
  - Removed dead commented-out debug `print` blocks.
  - Unified string quote style to double-quotes.
  - Added docstrings to `create_dataloader`, `preprocess`, `get_scaler`.
  - Removed unused `zipfile` import.
- `ohiot1dm_glucose_dataset/training_function.py` — comprehensive cleanup:
  - Removed redundant `path` variable.
  - Fixed learning-rate schedule: now mutates `optimizer.param_groups` (the
    original `lr /= 10` only mutated the local variable, not the optimiser).
  - Test dataloader now correctly uses `test_data_dirs` (not `train_data_dirs`).
  - Removed stale inline comments.
  - Added docstrings.
- `ohiot1dm_glucose_dataset/lstm_model.py` — cleanup:
  - Removed stray `# ... [SimpleLSTM class definition] ...` placeholder.
  - Fixed mixed 2-space / 4-space indentation.
  - Added class docstring.
- `scripts/convert2pfun.py` — fixed relative `Ohio Data/` path to use
  `_REPO_ROOT` so the script works from any working directory.
- `README.md` — fully rewritten to reflect the current project structure,
  new package API, quick-start instructions, and updated results table.

---

## [Unreleased] — 2026-08-02 (first pass)

### Added
- `notebooks/` directory to hold all Jupyter notebooks.
- `notebooks/01_lstm_glucose_exploration.ipynb` — the original Colab notebook,
  moved here from the repository root and renamed for clarity.
- `notebooks/02_comparison_lstm_vs_cma.ipynb` — new notebook comparing
  `SimpleLSTM` and the PFun CMA model across interpolation and forecasting,
  with regression metrics and glucose-zone confusion matrices.
- `flake.nix` — Nix dev-shell with Python 3.12, `uv`, and required system libs.
- `PATCH-NOTES.md` — this file.
- `AGENTS-TODO.md` — agent-maintained task list.

### Changed
- `pyproject.toml`:
  - Description updated.
  - `requires-python` tightened to `>=3.12,<3.13`.
  - Added `numpy`, `scipy` as explicit runtime dependencies.
  - Dev group expanded: `ipykernel`, `jupyter`, `nbformat`, `seaborn`.
  - Added `[tool.uv.sources]` for `pfun-cma-model`.
  - Added `[project.scripts]` entry-point `ohiot1dm-train`.
  - Added `[build-system]` (hatchling) and `[tool.hatch.build.targets.wheel]`.
- Python source files relocated into `ohiot1dm_glucose_dataset/` package.
- All intra-package imports updated to absolute package paths.
- `ohiot1dm_glucose_dataset/__init__.py` now exports the public API.
- `training_function.py` bug fix: undefined `lstm_model` → `model`.

### Removed
- `Gluc_proj_env.yaml` — superseded by `pyproject.toml` / `uv.lock`.
- `Glucese_proj_notebook.ipynb` (root) — moved to
  `notebooks/01_lstm_glucose_exploration.ipynb`.
