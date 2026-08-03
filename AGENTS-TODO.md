# Agents TODO

This file is maintained by the Copilot coding agent.
Check items off as they are completed; add new items as they are discovered.

---

## Open

- [ ] Enable GitHub Pages for the repository (Settings → Pages → Source:
      GitHub Actions) so `.github/workflows/pages.yml` can deploy.
- [ ] Add a `docs/Gemfile.lock` once `bundle install` has been run locally
      (requires a real Ruby/bundler toolchain; the dev shell's `bundle` is a
      stub at present).
- [ ] Validate the Jekyll site renders the new `docs/api/pfun-utils.md` page
      once `docs/Gemfile.lock` exists (`bundle exec jekyll serve`).
- [ ] Investigate the large MARD on LSTM rows: `get_scaler` fills missing
      `cbg` rows with `min - 0.01·|min|` before MinMax scaling, so
      `regression_metrics` MARD (`|Δ|/max(y_true, 1e-6)`) blows up on the
      filled rows (LSTM forecast MARD ≈ 2e6, interpolation ≈ 7e5). Masking
      low-`y_true` pairs or excluding filled rows needs a deliberate metric
      decision.

---

## Completed

- [x] Regenerate `uv.lock` after adding `pfun-cma-model` and new dev deps
      (verified: the lock pins `pfun-cma-model` at git commit `2819721...`).
- [x] Validate that `notebooks/02_comparison_lstm_vs_cma.ipynb` runs
      end-to-end (`uv run jupyter nbconvert --to notebook --execute`).
- [x] Port `notebooks/02_comparison_lstm_vs_cma.ipynb` onto the new
      `pfun_utils` helpers — `unscale_glucose` (replacing the broken 3-arg
      `normalize_glucose` call and the `G * 200` approximation),
      `collect_predictions` / `collect_interpolation`,
      `regression_metrics`, `glucose_zone`, `load_ohio_csv` / `fit_patient`;
      removed the local reimplementations and the dead `cma_unscale_glucose`.
- [x] Fix notebook 02 bugs surfaced during the port: the undefined
      `ma_yt_ip` typo (`cma_yt_ip`), the horizon wording (`N_STEPS_AHEAD`
      = 120 → 600 min), robust `REPO_ROOT` discovery, broken markdown
      placeholders in sections 4 and 10, and a stray `]` in the heatmap
      suptitle.
- [x] Batch the LSTM autoregressive forecast collection in notebook 02
      (one forward pass per step per batch instead of per sample) so the
      600-min horizon runs end-to-end without a `KeyboardInterrupt`.
- [x] Gitignore and untrack `.virtual_documents/` and `notebooks/*.pth`
      (JupyterLab scratch copies and regenerated training artifacts).

- [x] Move `Glucese_proj_notebook.ipynb` →
      `notebooks/01_lstm_glucose_exploration.ipynb`.
- [x] Move Python source files into `ohiot1dm_glucose_dataset/` package.
- [x] Fix all intra-package imports (absolute paths).
- [x] Fix `training_function.py` bug: undefined `lstm_model` → `model`.
- [x] Fix `training_function.py` LR schedule: mutate `optimizer.param_groups`
      instead of local variable.
- [x] Fix `training_function.py`: test dataloader now uses `test_data_dirs`.
- [x] Replace `os.getcwd()` path hacks with `Path(__file__).parents[N]`.
- [x] Remove duplicate `from pathlib import Path` in `data_processor_loader.py`.
- [x] Remove dead commented-out debug `print` blocks.
- [x] Clean up mixed indentation in `lstm_model.py`.
- [x] Fix `scripts/convert2pfun.py` relative path.
- [x] Update `pyproject.toml`: description, deps, build-system, entry-point,
      `pfun-cma-model` uv source.
- [x] Remove `Gluc_proj_env.yaml`.
- [x] Create `flake.nix` with Nix dev-shell.
- [x] Create `notebooks/02_comparison_lstm_vs_cma.ipynb`.
- [x] Rewrite `README.md` for new project layout.
- [x] Set up Jekyll documentation site (`docs/`) with Just the Docs theme.
- [x] Add `.github/workflows/pages.yml` for GitHub Pages deployment.
- [x] Update `PATCH-NOTES.md` with both rounds of changes.
- [x] Update `AGENTS-TODO.md` (this file).
- [x] Add `pfun_utils.py` backend module bridging OhioT1DM CSVs to
      `pfun-cma-model` (load/convert/fit/unscale/metrics helpers).
- [x] Rewrite `scripts/convert2pfun.py` as a pfun-conversion argparse CLI
      (`--list`, `--convert`, `--fit`, `--metrics`, `--N`, `--units`,
      `--format`, `--n-steps`, `--outdir`).
- [x] Extend `ohiot1dm_glucose_dataset/__init__.py` exports with the
      `pfun_utils` API.
- [x] Document the pfun compatibility backend: `docs/api/pfun-utils.md`,
      `docs/getting-started.md`, `docs/api/index.md`, `PATCH-NOTES.md`.
- [x] Code-review fixes for the pfun backend: `load_ohio_csv` returns a
      plain DataFrame, phase-aware time axis, mgdl-only `unscale_glucose`,
      resilient `--convert`, CLI boundary validation.
- [x] Update docs to the reviewed pfun API: `docs/api/pfun-utils.md`,
      `docs/getting-started.md`, `PATCH-NOTES.md`.
