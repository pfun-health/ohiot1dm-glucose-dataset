# Agents TODO

This file is maintained by the Copilot coding agent.
Check items off as they are completed; add new items as they are discovered.

---

## Open

- [ ] Regenerate `uv.lock` after adding `pfun-cma-model` and new dev deps.
      (Requires network access: `uv lock`.)
- [ ] Enable GitHub Pages for the repository (Settings → Pages → Source:
      GitHub Actions) so `.github/workflows/pages.yml` can deploy.
- [ ] Validate that `notebooks/02_comparison_lstm_vs_cma.ipynb` runs
      end-to-end once `pfun-cma-model` is installed (`uv sync --dev`).
- [ ] Add a `docs/Gemfile.lock` once `bundle install` has been run locally.

---

## Completed

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
