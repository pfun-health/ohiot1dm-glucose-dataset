---
layout: default
title: Development
nav_order: 6
---

# Development
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Project layout

```
ohiot1dm-glucose-dataset/
├── .python-version              # Python 3.12
├── flake.nix                    # Nix dev-shell
├── pyproject.toml               # uv project metadata + dependencies
├── uv.lock                      # locked dependency graph
├── PATCH-NOTES.md               # changelog
├── AGENTS-TODO.md               # open tasks
├── README.md
├── Report.md
├── Images/
├── Ohio Data/                   # dataset (not committed)
├── notebooks/
│   ├── 01_lstm_glucose_exploration.ipynb
│   └── 02_comparison_lstm_vs_cma.ipynb
├── ohiot1dm_glucose_dataset/    # Python package
│   ├── __init__.py
│   ├── data_processor_loader.py
│   ├── lstm_model.py
│   ├── training_function.py
│   └── main.py
├── scripts/
│   ├── convert2parquet.sh
│   └── convert2pfun.py
└── docs/                        # this site
```

---

## Dependencies

Runtime dependencies are declared in `pyproject.toml`.
`pfun-cma-model` is sourced directly from its GitHub repository:

```toml
[tool.uv.sources]
pfun-cma-model = { git = "https://github.com/pfun-health/pfun-cma-model" }
```

Dev dependencies (Jupyter, ipykernel, seaborn, nbformat) are in the
`[dependency-groups] dev` group and installed with `uv sync --dev`.

To update the lock file after editing `pyproject.toml`:

```bash
uv lock
```

---

## Nix dev-shell

`flake.nix` provides a reproducible development shell containing Python 3.12,
`uv`, and the necessary system libraries:

```bash
# Enter the dev-shell
nix develop

# Or with direnv
echo "use flake" > .envrc && direnv allow
```

---

## Conventional commits

Please use
[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) for
commit messages:

| Type | When to use |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `chore` | Build, CI, dependency updates |
| `nb` | Notebook changes |

---

## Building the docs locally

```bash
cd docs/
bundle install
bundle exec jekyll serve --livereload
# → open http://localhost:4000/ohiot1dm-glucose-dataset/
```

---

## GitHub Pages deployment

The site is built automatically by `.github/workflows/pages.yml` on every push
to `main`.  The workflow:

1. Checks out the repository.
2. Sets up Ruby and installs the Gemfile.
3. Builds the Jekyll site from `docs/`.
4. Deploys to GitHub Pages via `actions/deploy-pages`.
