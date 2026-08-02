# Agents TODO

This file is maintained by the Copilot coding agent.
Check items off as they are completed; add new items as they are discovered.

---

## In Progress / Open

- [ ] Regenerate `uv.lock` after adding `pfun-cma-model` and new dev deps to
      `pyproject.toml`.  (Requires network access to PyPI / GitHub; must be
      done by a developer with the full environment: `uv lock`.)
- [ ] Validate that the notebook `02_comparison_lstm_vs_cma.ipynb` runs
      end-to-end once `pfun-cma-model` is installed (`uv sync --dev`).
- [ ] Add a `notebooks/README.md` briefly describing each notebook.
- [ ] Update the root `README.md` to reflect the new project structure
      (package layout, `flake.nix`, notebooks directory, `uv` usage).

---

## Completed

- [x] Move `Glucese_proj_notebook.ipynb` →
      `notebooks/01_lstm_glucose_exploration.ipynb`.
- [x] Move Python source files into `ohiot1dm_glucose_dataset/` package.
- [x] Fix all intra-package imports (absolute paths).
- [x] Fix `training_function.py` bug: undefined `lstm_model` → `model`.
- [x] Replace `os.getcwd()` path hacks with `Path(__file__).parents[N]`.
- [x] Update `pyproject.toml`: description, deps, build-system, entry-point,
      `pfun-cma-model` uv source.
- [x] Remove `Gluc_proj_env.yaml`.
- [x] Create `flake.nix` with Nix dev-shell.
- [x] Create `notebooks/02_comparison_lstm_vs_cma.ipynb` with confusion
      matrix, regression metrics, and LSTM vs CMA comparison.
- [x] Create `PATCH-NOTES.md`.
- [x] Create `AGENTS-TODO.md` (this file).
