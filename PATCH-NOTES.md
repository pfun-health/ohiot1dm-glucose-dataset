# Patch Notes

All notable changes to this project are documented here.
Format is inspired by [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased] — 2026-08-03 (fourth pass)

### Changed
- `notebooks/02_comparison_lstm_vs_cma.ipynb` — ported onto the
  `pfun_utils` helpers:
  - CMA fitting now uses `pfun_utils.fit_patient` (phase-aware UTC time
    axis, `missing_cbg` filtering, mgdl-normalized fit) and the collectors
    `collect_predictions` / `collect_interpolation`.
  - CMA unscaling uses `unscale_glucose` (numeric sigmoid inversion) instead
    of the broken three-argument `normalize_glucose` call and the
    `G * 200` approximation; the dead `cma_unscale_glucose` helper and the
    local `regression_metrics` / `glucose_zone` / `zone_metrics` /
    `load_ohio_csv` reimplementations were removed in favour of the library
    helpers.
  - Fixed the undefined `ma_yt_ip` typo (`cma_yt_ip`), the horizon wording
    (`N_STEPS_AHEAD = 120` → 600 min), the `REPO_ROOT` discovery (walk up
    to the `Ohio Data/` folder instead of the `Path("__file__")` trick),
    broken markdown placeholders in sections 4 and 10, and a stray `]` in
    the heatmap suptitle.
  - The LSTM forecast collection is now batched (one forward pass per step
    per batch) so the 600-min horizon runs end-to-end without a
    `KeyboardInterrupt`; semantics are unchanged (one point pair per sample:
    the prediction at `n_steps` ahead versus the observed value).
  - Validated end-to-end: `uv run jupyter nbconvert --to notebook --execute`
    completes cleanly — 12 CMA fits (559 residual 50.2209, matching the
    phase-aware time axis), LSTM forecasting 34 181 samples, CMA forecasting
    2 016 samples, CMA interpolation 0 (documented empty), fresh
    regression/zone outputs.

### Removed
- `.virtual_documents/` scratch copies (JupyterLab virtual documents, now
  gitignored) and the tracked `notebooks/*.pth` checkpoints (training
  artifacts, now gitignored).

---

## [Unreleased] — 2026-08-02 (third pass)

### Added
- `ohiot1dm_glucose_dataset/pfun_utils.py` — new module bridging OhioT1DM
  processed CSVs to the `pfun-cma-model` package:
  - `load_ohio_csv` — read a CSV, attach a tz-aware UTC 5-minute time axis
    anchored at `2020-01-01`, and set the `sg` / `value` glucose columns.
  - `convert_ohio_to_pfun` — drop `missing_cbg != 0` rows and return pfun's
    `format_data` representation (`time, value, tod, t, G`, `G` in `[0, 2]`).
  - `fit_patient` / `fit_patients` — fit the CMA model to one or many CSVs
    (per-file try/except in the batch helper).
  - `unscale_glucose` — numerically invert pfun's saturating
    `normalize_glucose` sigmoid back to mg/dL.
  - `collect_predictions` / `collect_interpolation` — forecast arrays in
    normalized space; interpolation deliberately returns empty arrays.
  - `regression_metrics` / `glucose_zone` / `zone_metrics` — RMSE/MAE/MARD/R²
    and a clinical glucose-zone confusion matrix.
- `docs/api/pfun-utils.md` — API reference for the new module, linked from
  `docs/api/index.md` and `docs/getting-started.md`.

### Changed
- `scripts/convert2pfun.py` — rewritten as a pfun-conversion CLI:
  `--list`, `--convert`, `--fit`, `--metrics`, `--N`, `--units`, `--format`,
  `--n-steps`, `--outdir`. (Previously: an LSTM-scaled markdown dump.)
- `ohiot1dm_glucose_dataset/__init__.py` — exports extended with the full
  `pfun_utils` API.

### Design decisions
- **Correct sigmoid inverse.** `unscale_glucose` inverts
  `normalize_glucose` with `scipy.optimize.brentq` and returns the
  saturation onset (~221 mg/dL) for ceiling targets, replacing the
  comparison notebook's broken three-argument `normalize_glucose` call and
  its `G * 200` approximation.
- **No module-level globals.** Every function is pure; only frozen constants
  (`HYPO_THRESHOLD`, `HYPER_THRESHOLD`, `ZONE_LABELS`, `_REFERENCE_TIME`)
  live at module scope.
- **Empty interpolation is documented behaviour.** OhioT1DM missing rows
  carry NaN `cbg`, so there is no ground truth to score interpolation
  against; `collect_interpolation` warns and returns empty arrays instead of
  fabricating values.
- **Lazy pfun imports.** `pfun-cma-model` stays a dev dependency; importing
  the package never requires it, and any function needing pfun raises a
  helpful `ImportError` (pointing at `uv sync --dev`) when it is missing.
- **No `tabulate` dependency.** CLI tables are rendered with f-strings and
  pandas `to_string()`.

### Review fixes
- `load_ohio_csv` now returns just the augmented `pd.DataFrame` (the earlier
  `(df, sg_min, sg_max)` tuple is gone) and validates input at the boundary:
  `cbg` / `missing_cbg` must be present and the file must be non-empty.
- Time axis is phase-aware: anchored at `2020-01-01` UTC plus
  `5 min * (first 5minute_intervals_timestamp % 288)`. Every test counter's
  integer part is an exact multiple of 288 (the midnight-UTC epoch), so
  `first_counter % 288` derives the true sub-interval time-of-day phase:
  559/563 → 0.2 (1 min), 570 → 0.8 (4 min), 591 → 0.6 (3 min), and 4 of
  the 6 Ohio2020 files have phases up to 4.35 min; only 575/588 are exactly
  0. Residuals stay identical for 575/588 while phased files shift slightly
  (e.g., 559-ws-testing 50.0297 → 50.2209), so the notebook's published 559
  residual now legitimately differs from the library's output.
- `unscale_glucose` is mgdl-only; any other `units` raises `ValueError`
  because the OhioT1DM pipeline fits in mgdl-normalized space and pfun's
  mmoll normalize curve is degenerate.
- `--convert` is resilient: per-file failures print `FAILED:` lines and the
  run finishes with `Wrote k of n file(s).`
- CLI `--units` choices are `["mgdl"]` only; `--N` and `--n-steps` are
  validated as positive integers; `--outdir` is created as needed.
- Lazy pfun imports create `logs/` first and chain the underlying exception
  into the `ImportError`.

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
