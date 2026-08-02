---
layout: default
title: PFun CMA Compatibility
parent: API Reference
nav_order: 4
---

# PFun CMA Compatibility
{: .no_toc }

**Module:** `ohiot1dm_glucose_dataset.pfun_utils`

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## OhioT1DM → pfun pipeline

This module bridges the raw OhioT1DM processed CSVs to the
[`pfun-cma-model`](https://github.com/pfun-health/pfun-cma-model) package:

1. `load_ohio_csv` reads a CSV and attaches the time axis and column names
   pfun recognises (`time`, `displayTime` / `systemTime`, `sg`, `value`).
2. `convert_ohio_to_pfun` drops rows with missing glucose and returns pfun's
   `format_data` representation (`time, value, tod, t, G`, with `G`
   normalized to `[0, 2]`).
3. `fit_patient` / `fit_patients` fit the CMA model and return
   `CMAFitResult` objects.
4. `collect_predictions` aligns observed vs. predicted values for a forecast
   horizon, still in normalized `[0, 2]` space.
5. `unscale_glucose` converts those normalized values back to mg/dL (the
   only supported unit), and `regression_metrics`, `glucose_zone`, and
   `zone_metrics` score the results.

> **Optional dependency:** `pfun-cma-model` is a *dev* dependency, not a
> runtime dependency. Importing `ohiot1dm_glucose_dataset` never requires it;
> each function that needs pfun imports it lazily and raises a helpful
> `ImportError` (pointing at `uv sync --dev`) if it is missing. Because pfun's
> logging setup opens `logs/` relative to the CWD at import time, the lazy
> importer creates that directory as a fallback first, and the `ImportError`
> chains the underlying exception so callers can tell "not installed" from
> "import crashed".

---

## load_ohio_csv

```python
def load_ohio_csv(fpath: str | Path) -> pd.DataFrame
```

Reads one OhioT1DM processed CSV and attaches the columns pfun requires. The
input is validated at the boundary: the `cbg` / `missing_cbg` columns must be
present and the file must be non-empty; failures raise a descriptive
`ValueError` naming the file.

- `time` — a tz-aware UTC `DatetimeIndex` at 5-minute cadence. The axis is
  anchored at `2020-01-01` (an arbitrary reference date) plus the counter's
  actual phase, `5 min * (first 5minute_intervals_timestamp % 288)`, so
  files that do not start exactly at midnight keep their true time-of-day.
- `displayTime` / `systemTime` — aliases of `time`.
- `sg = cbg` and `value = sg` — the glucose columns pfun recognises.

**Parameters**

| Name | Type | Description |
|---|---|---|
| `fpath` | `str \| Path` | Path to a processed OhioT1DM CSV |

**Returns** the augmented DataFrame (a plain `pd.DataFrame` — no tuple).

---

## convert_ohio_to_pfun

```python
def convert_ohio_to_pfun(
    fpath: str | Path,
    N: int = 288,
    tz_offset: float | None = None,
) -> pd.DataFrame
```

Converts one OhioT1DM CSV to pfun's formatted representation. Rows with
`missing_cbg != 0` (NaN glucose) are dropped before calling
`pfun_cma_model.engine.data_utils.format_data`.

**Parameters**

| Name | Type | Default | Description |
|---|---|---|---|
| `fpath` | `str \| Path` | — | Path to a processed OhioT1DM CSV |
| `N` | `int` | `288` | Number of model output samples |
| `tz_offset` | `float \| None` | `None` | Optional UTC offset passed through to `format_data` |

**Returns** a DataFrame with columns `time, value, tod, t, G`, indexed by
`t`.

---

## fit_patient

```python
def fit_patient(
    fpath: str | Path,
    N: int = 288,
    **fit_kwds: Any,
) -> CMAFitResult
```

Fits the CMA model to one OhioT1DM patient CSV. Rows with `missing_cbg != 0`
are dropped first; the remaining rows are passed to
`pfun_cma_model.engine.fit.fit_model` with `tcol="time"` and `ycol="G"`.

**Parameters**

| Name | Type | Default | Description |
|---|---|---|---|
| `fpath` | `str \| Path` | — | Path to a processed OhioT1DM CSV |
| `N` | `int` | `288` | Number of model output samples |
| `fit_kwds` | `Any` | — | Extra keyword arguments forwarded to `fit_model` |

**Returns** a `pfun_cma_model.engine.fit.CMAFitResult`.

---

## fit_patients

```python
def fit_patients(
    data_dirs: list[str | Path],
    N: int = 288,
    **fit_kwds: Any,
) -> dict[Path, CMAFitResult]
```

Fits CMA to every CSV under each of the given directories. Each directory is
scanned with `sorted(Path(d).glob("*.csv"))`; a file that fails to fit is
reported to stdout and skipped, so one bad file does not abort the batch.

**Parameters**

| Name | Type | Default | Description |
|---|---|---|---|
| `data_dirs` | `list[str \| Path]` | — | Directories to scan for `*.csv` files |
| `N` | `int` | `288` | Number of model output samples |
| `fit_kwds` | `Any` | — | Extra keyword arguments forwarded to `fit_model` |

**Returns** a dict mapping every successfully fitted CSV path to its
`CMAFitResult`.

---

## unscale_glucose

```python
def unscale_glucose(
    g_norm: np.ndarray,
    units: str = "mgdl",
) -> np.ndarray
```

Inverts pfun's `normalize_glucose` by numeric root-finding
(`scipy.optimize.brentq`), because the forward map is a strictly increasing
sigmoid without a closed-form inverse. Only `units="mgdl"` is supported: the
OhioT1DM pipeline fits in mgdl-normalized space (pfun's
`guess_glucose_units` picks mgdl for Ohio data), and pfun's mmoll normalize
curve is degenerate — the whole clinical range compresses into normalized
`[0.985, 2.0]`, saturating only near ~57.5 mmol/L — so inverting with it
would be silently wrong. The bracketing interval is `[30, 600]` mg/dL.

Two edge cases are handled explicitly because the forward map saturates in
float64:

- Targets at or above the ceiling (`normalize_glucose` returns exactly `2.0`
  for every glucose above the saturation onset, ~221 mg/dL) map to the
  *onset* — the smallest glucose that achieves the ceiling — as the
  least-misleading single value.
- Targets below the floor achievable inside the bracket are clamped to the
  lower bracket edge. NaN propagates.

Raises `ValueError` for any `units` other than `"mgdl"`.

---

## collect_predictions

```python
def collect_predictions(
    results: dict[Path, CMAFitResult],
    n_steps: int,
) -> tuple[np.ndarray, np.ndarray]
```

Builds `(y_true, y_pred)` arrays in **normalized `[0, 2]` space**. The model
prediction is shifted `n_steps` model-grid steps ahead and aligned with the
observed values: true at step `t + n` versus prediction at step `t`. Files
too short for the horizon are skipped; callers decide whether to unscale the
result (see `unscale_glucose`).

**Parameters**

| Name | Type | Description |
|---|---|---|
| `results` | `dict[Path, CMAFitResult]` | Fitted results from `fit_patients` |
| `n_steps` | `int` | Forecast horizon in model-grid steps |

**Returns** `(y_true, y_pred)` concatenated across all fitted files, or two
empty arrays if nothing could be aligned.

---

## collect_interpolation

```python
def collect_interpolation(
    results: dict[Path, CMAFitResult],
) -> tuple[np.ndarray, np.ndarray]
```

Always returns empty arrays. OhioT1DM rows with `missing_cbg == 1` carry NaN
`cbg`, so there is no observed value to score an interpolation against;
fabricating one would be misleading. Emits a `UserWarning` explaining this.

---

## regression_metrics

```python
def regression_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
) -> dict[str, float]
```

Regression metrics ported from the comparison notebook. NaN pairs are masked
out first; an empty remainder returns NaN for every key.

**Returns** a dict with keys `N` (count, as float), `RMSE`, `MAE`, `MARD`,
`R²`.

---

## glucose_zone

```python
def glucose_zone(values: np.ndarray) -> np.ndarray
```

Maps mg/dL values to clinical glucose zones using the module thresholds:

| Label | Range |
|---|---|
| `Hypo (<70)` | `< 70` mg/dL |
| `Euglycemia` | `70–180` mg/dL |
| `Hyper (>180)` | `> 180` mg/dL |

**Returns** an object array of zone labels, one per input value.

---

## zone_metrics

```python
def zone_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
) -> pd.DataFrame
```

Glucose-zone confusion matrix computed with `sklearn.metrics.confusion_matrix`
(rows = true, columns = predicted). NaN pairs are masked out before the zones
are computed.

**Returns** a DataFrame labelled with `ZONE_LABELS` on both axes.

---

## Module constants

| Name | Value | Description |
|---|---|---|
| `HYPO_THRESHOLD` | `70.0` | Clinical hypoglycemia threshold (mg/dL) |
| `HYPER_THRESHOLD` | `180.0` | Clinical hyperglycemia threshold (mg/dL) |
| `ZONE_LABELS` | `("Hypo (<70)", "Euglycemia", "Hyper (>180)")` | Zone labels, ordered for `confusion_matrix` |
