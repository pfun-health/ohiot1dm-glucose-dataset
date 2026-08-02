---
layout: default
title: Data Loading
parent: API Reference
nav_order: 1
---

# Data Loading
{: .no_toc }

**Module:** `ohiot1dm_glucose_dataset.data_processor_loader`

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## OhioT1DMDataset

```python
class OhioT1DMDataset(torch.utils.data.Dataset):
    def __init__(self, data_dirs: list[str], seq_length: int) -> None
```

A `torch.utils.data.Dataset` that loads, merges, preprocesses, and serves
fixed-length sequences from the OhioT1DM CSV files.

**Parameters**

| Name | Type | Description |
|---|---|---|
| `data_dirs` | `list[str]` | Directories to scan recursively for `*.csv` files |
| `seq_length` | `int` | Total sequence length (context + target steps) |

**Attributes**

| Name | Type | Description |
|---|---|---|
| `scaler` | `MinMaxScaler` | Fitted scaler (fit on the merged data) |
| `preprocessed_dfs` | `list[pd.DataFrame]` | One scaled DataFrame per source CSV |
| `data` | `list[torch.Tensor]` | Tensor version of each preprocessed DataFrame |

**`__getitem__`** returns `(inputs, target)`:
- `inputs` — shape `(seq_length - 1, n_features)`
- `target` — shape `(n_features,)` — the last time step of the sequence

---

## create_dataloader

```python
def create_dataloader(
    data_dirs: list[str],
    seq_length: int,
    batch_size: int,
) -> torch.utils.data.DataLoader
```

Convenience factory: instantiates `OhioT1DMDataset` and wraps it in a
`DataLoader`.  Also attaches an `unscale(data)` function to the returned
loader so predictions can be converted back to mg/dL.

**`unscale(data: torch.Tensor) → torch.Tensor`**

Inverts the MinMax scaling.  Input shape: `(1, seq, n_features)` or
`(batch, seq, n_features)`.

---

## preprocess

```python
def preprocess(
    scaler: MinMaxScaler,
    fill_values: pd.Series,
    data_df: pd.DataFrame,
) -> pd.DataFrame
```

Pre-processes a single patient DataFrame:

1. Identifies rows where `missing_cbg == 1`.
2. Imputes `cbg` via cubic spline interpolation.
3. Drops `5minute_intervals_timestamp` and `missing_cbg`.
4. Moves `cbg` to the last column.
5. Fills remaining NaNs with `fill_values`.
6. Applies `scaler.transform`.

---

## get_scaler

```python
def get_scaler(data_df: pd.DataFrame) -> tuple[MinMaxScaler, pd.Series]
```

Fits a `MinMaxScaler` on the *merged* training DataFrame.
Also computes `fill_values` (per-column `min − 1 % × |min|`) used to
replace NaNs before scaling.

Returns `(scaler, fill_values)`.
