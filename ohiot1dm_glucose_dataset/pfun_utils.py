"""Bridge OhioT1DM raw CSVs to the ``pfun-cma-model`` package.

Every function here is pure: no module-level mutable state is used, and pfun
is imported lazily inside each function so that ``import ohiot1dm_glucose_dataset``
never requires pfun to be installed (pfun lives in the dev dependency group).
"""

from __future__ import annotations

import importlib
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from pfun_cma_model.engine.fit import CMAFitResult

#: Clinical glucose-zone thresholds (mg/dL).
HYPO_THRESHOLD = 70.0
HYPER_THRESHOLD = 180.0
#: Glucose-zone labels, ordered for ``sklearn.metrics.confusion_matrix``.
ZONE_LABELS = ("Hypo (<70)", "Euglycemia", "Hyper (>180)")

#: Arbitrary reference date used to build the 5-minute time axis (UTC).
_REFERENCE_TIME = pd.Timestamp("2020-01-01", tz="UTC")

_PFUN_IMPORT_HELP = (
    "pfun-cma-model is required for this function. "
    "Install dev dependencies with 'uv sync --dev'."
)


def _load_pfun_module(module_name: str) -> Any:
    """Lazily import ``pfun_cma_model.<module_name>`` with a helpful error.

    pfun's logging setup opens ``logs/`` relative to the CWD at import time,
    so that directory is created as a fallback before importing (library
    callers should not need a ``logs/`` directory in their CWD). Any other
    exception is re-raised as an ``ImportError`` chaining the underlying
    cause, so callers can distinguish "not installed" from "import crashed".
    """
    try:
        Path("logs").mkdir(exist_ok=True)
    except OSError:
        pass
    try:
        return importlib.import_module(f"pfun_cma_model.{module_name}")
    except Exception as exc:  # noqa: BLE001 - surface any import failure helpfully
        raise ImportError(f"{_PFUN_IMPORT_HELP} Import failed with: {exc}") from exc


def load_ohio_csv(fpath: str | Path) -> pd.DataFrame:
    """Read one OhioT1DM processed CSV and attach the pfun-required columns.

    Validates the file at the boundary: the ``cbg``/``missing_cbg`` columns
    must be present and the file must be non-empty; failures raise a
    descriptive ``ValueError`` naming the file.

    The 5-minute cadence is rebuilt from an arbitrary UTC reference date
    (``2020-01-01``) plus the counter's actual phase, so pfun can compute
    time-of-day, exactly like the comparison notebook recipe:

    - ``time``: tz-aware UTC ``DatetimeIndex`` (5-minute steps), anchored at
      ``2020-01-01`` + ``5 min * (first_counter % 288)`` so files that do not
      start exactly at midnight keep their true time-of-day
    - ``displayTime`` / ``systemTime``: aliases of ``time``
    - ``sg = cbg`` and ``value = sg``: glucose columns pfun recognises
    """
    try:
        df = pd.read_csv(fpath)
    except pd.errors.EmptyDataError as exc:
        raise ValueError(f"{fpath}: file is empty") from exc
    if not {"cbg", "missing_cbg", "5minute_intervals_timestamp"} <= set(df.columns):
        raise ValueError(
            f"{fpath}: missing required columns "
            "cbg/missing_cbg/5minute_intervals_timestamp"
        )
    if len(df) == 0:
        raise ValueError(f"{fpath}: file is empty")
    n = len(df)
    first_counter = float(df["5minute_intervals_timestamp"].iloc[0])
    phase_minutes = round(5.0 * (first_counter % 288.0), 3)
    start = _REFERENCE_TIME + pd.Timedelta(minutes=phase_minutes)
    df["time"] = pd.date_range(start=start, periods=n, freq="5min")
    df["displayTime"] = df["time"]
    df["systemTime"] = df["time"]
    df["sg"] = df["cbg"]
    df["value"] = df["sg"]
    return df


def convert_ohio_to_pfun(
    fpath: str | Path, N: int = 288, tz_offset: float | None = None
) -> pd.DataFrame:
    """Convert one OhioT1DM CSV to pfun's formatted representation.

    Rows with ``missing_cbg != 0`` (NaN glucose) are dropped before calling
    :func:`pfun_cma_model.engine.data_utils.format_data`. Returns the formatted
    DataFrame with columns ``time, value, tod, t, G`` indexed by ``t``.
    """
    df = load_ohio_csv(fpath)
    df_clean = df[df["missing_cbg"] == 0].copy()
    format_data = _load_pfun_module("engine.data_utils").format_data
    return format_data(df_clean, N=N, tz_offset=tz_offset)


def fit_patient(
    fpath: str | Path, N: int = 288, **fit_kwds: Any
) -> "CMAFitResult":
    """Fit the CMA model to one OhioT1DM patient CSV.

    Rows with ``missing_cbg != 0`` are dropped first; the remaining rows are
    passed to :func:`pfun_cma_model.engine.fit.fit_model` with
    ``tcol="time"`` and ``ycol="G"``. Returns a ``CMAFitResult``.
    """
    df = load_ohio_csv(fpath)
    df_clean = df[df["missing_cbg"] == 0].copy()
    fit_model = _load_pfun_module("engine.fit").fit_model
    return fit_model(df_clean, tcol="time", ycol="G", N=N, **fit_kwds)


def fit_patients(
    data_dirs: list[str | Path], N: int = 288, **fit_kwds: Any
) -> dict[Path, "CMAFitResult"]:
    """Fit CMA to every CSV under each of the given directories.

    Each directory is scanned with ``sorted(Path(d).glob("*.csv"))``. A file
    that fails to fit is reported to stdout (mirroring the notebook loop) and
    skipped; the returned dict maps every successfully fitted CSV to its result.
    """
    csv_paths = sorted(
        path
        for data_dir in data_dirs
        for path in Path(data_dir).glob("*.csv")
    )
    results: dict[Path, "CMAFitResult"] = {}
    for path in csv_paths:
        print(f"  Fitting CMA to {path.name} ...")
        try:
            result = fit_patient(path, N=N, **fit_kwds)
        except Exception as exc:  # noqa: BLE001 - one bad file must not abort the batch
            print(f"  FAILED {path.name}: {exc}")
        else:
            results[path] = result
    return results


def unscale_glucose(g_norm: np.ndarray, units: str = "mgdl") -> np.ndarray:
    """Invert pfun's :func:`normalize_glucose` via numeric root-finding.

    pfun normalizes raw glucose to ``[0, 2]`` through a strictly increasing
    sigmoid; its closed-form inverse does not exist, so each element is solved
    with :func:`scipy.optimize.brentq` against
    ``normalize_glucose(g, "mgdl") - g_norm_i == 0``.

    Only ``units="mgdl"`` is supported: the OhioT1DM pipeline fits in
    mgdl-normalized space (:func:`guess_glucose_units` picks mgdl for Ohio
    data), and pfun's mmoll normalize curve is degenerate (the whole clinical
    range compresses into normalized ``[0.985, 2.0]``, saturating only near
    ~57.5 mmol/L), so inverting with it would be silently wrong. Any other
    ``units`` value raises ``ValueError``.

    The bracketing interval is ``[30, 600]`` mg/dL. Two edge cases are
    handled explicitly because the forward map saturates in float64:

    - Targets at or above the ceiling (``normalize_glucose`` returns exactly
      ``2.0`` for every glucose above the saturation onset, ~221 mg/dL): the
      preimage is a plateau, so the *onset* (smallest glucose achieving that
      ceiling) is returned — the least-misleading single value.
    - Targets below the floor achievable inside the bracket: clamped to the
      lower bracket edge. NaN propagates.
    """
    if units != "mgdl":
        raise ValueError(
            f"unscale_glucose only supports units='mgdl'; got {units!r}. "
            "The OhioT1DM pipeline fits in mgdl-normalized space and pfun's "
            "mmoll normalize curve is degenerate, so mmoll inversion is not "
            "supported."
        )

    from scipy.optimize import brentq

    normalize_glucose = _load_pfun_module("engine.data_utils").normalize_glucose
    lo, hi = 30.0, 600.0

    def normed(g: float) -> float:
        """Single-value wrapper around pfun's normalize_glucose."""
        return float(normalize_glucose(np.array([g]), units)[0])

    values = np.asarray(g_norm, dtype=float)
    out = np.empty(values.shape, dtype=float)
    f_lo, f_hi = normed(lo), normed(hi)

    # Float64 saturation onset: smallest glucose whose normalized value
    # already rounds up to the ceiling f_hi (found by bisection).
    onset_lo, onset_hi = lo, hi
    while onset_hi - onset_lo > 1e-12:
        mid = 0.5 * (onset_lo + onset_hi)
        if normed(mid) >= f_hi:
            onset_hi = mid
        else:
            onset_lo = mid
    saturation_onset = onset_hi

    for index, target in np.ndenumerate(values):
        if np.isnan(target):
            out[index] = np.nan
            continue
        if target >= f_hi:
            out[index] = saturation_onset
            continue
        target_clamped = max(target, f_lo)
        f = lambda g: normed(g) - target_clamped  # noqa: E731
        out[index] = brentq(f, lo, hi, xtol=1e-12)
    return out


def collect_predictions(
    results: dict[Path, "CMAFitResult"], n_steps: int
) -> tuple[np.ndarray, np.ndarray]:
    """Build ``(y_true, y_pred)`` arrays in NORMALIZED ``[0, 2]`` space.

    For forecasting, the model prediction is shifted ``n_steps`` model-grid
    steps ahead and aligned with the observed values: true at step ``t+n``
    versus prediction at step ``t``. The model grid ``soln`` spans time-of-day
    on ``linspace(0, 24, N)``, so ``n_steps`` counts grid points (only ~5
    minutes apart for a single-day ``N=288`` grid; multi-day files are
    downsampled to ``N=288`` points across the whole span). Callers decide
    whether to unscale the result (see :func:`unscale_glucose`).
    """
    if n_steps < 1:
        raise ValueError("n_steps must be >= 1")
    y_true_all: list[np.ndarray] = []
    y_pred_all: list[np.ndarray] = []
    for result in results.values():
        g_pred = result.soln["G"].to_numpy()
        g_true = result.formatted_data["G"].to_numpy()
        min_len = min(len(g_pred) - n_steps, len(g_true) - n_steps)
        if min_len <= 0:
            continue
        y_true_all.append(g_true[n_steps : n_steps + min_len])
        y_pred_all.append(g_pred[:min_len])
    if not y_true_all:
        return np.array([]), np.array([])
    return np.concatenate(y_true_all), np.concatenate(y_pred_all)


def collect_interpolation(
    results: dict[Path, "CMAFitResult"],
) -> tuple[np.ndarray, np.ndarray]:
    """Return empty arrays: OhioT1DM has no ground truth for interpolation.

    Rows with ``missing_cbg == 1`` carry NaN ``cbg``, so there is no observed
    value to score an interpolation against; fabricating one would be
    misleading, so this always warns and returns empty arrays.
    """
    warnings.warn(
        "OhioT1DM rows with missing_cbg == 1 have NaN cbg, so there is no "
        "ground truth to evaluate interpolation against; returning empty "
        "arrays.",
        stacklevel=2,
    )
    return np.array([]), np.array([])


def regression_metrics(
    y_true: np.ndarray, y_pred: np.ndarray
) -> dict[str, float]:
    """Return regression metrics, ported from the comparison notebook.

    NaN pairs are masked out first; an empty remainder returns NaNs for every
    key. Keys: ``N`` (count, as float), ``RMSE``, ``MAE``, ``MARD``, ``R²``.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    mask = ~(np.isnan(y_true) | np.isnan(y_pred))
    y_true, y_pred = y_true[mask], y_pred[mask]
    if len(y_true) == 0:
        return {key: float("nan") for key in ["N", "RMSE", "MAE", "MARD", "R²"]}

    mse = float(np.mean((y_true - y_pred) ** 2))
    mae = float(np.mean(np.abs(y_true - y_pred)))
    mard = float(np.mean(np.abs(y_true - y_pred) / np.maximum(y_true, 1e-6)))
    ss_res = float(np.sum((y_true - y_pred) ** 2))
    ss_tot = float(np.sum((y_true - np.mean(y_true)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return {
        "N": float(len(y_true)),
        "RMSE": float(np.sqrt(mse)),
        "MAE": mae,
        "MARD": mard,
        "R²": r2,
    }


def glucose_zone(values: np.ndarray) -> np.ndarray:
    """Map mg/dL values to clinical glucose zones (``HYPO``/``HYPER`` thresholds).

    NaN values are NOT labelled: both comparisons are ``False`` for NaN, so a
    NaN element silently falls through to the ``"Euglycemia"`` label. Callers
    that must not label missing data should mask NaN first (as
    :func:`zone_metrics` does).
    """
    values = np.asarray(values)
    labels = np.full(len(values), "Euglycemia", dtype=object)
    labels[values < HYPO_THRESHOLD] = "Hypo (<70)"
    labels[values > HYPER_THRESHOLD] = "Hyper (>180)"
    return labels


def zone_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> pd.DataFrame:
    """Return a glucose-zone confusion matrix (rows=true, cols=predicted).

    NaN pairs are masked out before the zones are computed; the matrix is
    labelled with :data:`ZONE_LABELS` on both axes.
    """
    from sklearn.metrics import confusion_matrix

    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    mask = ~(np.isnan(y_true) | np.isnan(y_pred))
    zones_true = glucose_zone(y_true[mask])
    zones_pred = glucose_zone(y_pred[mask])
    matrix = confusion_matrix(zones_true, zones_pred, labels=ZONE_LABELS)
    return pd.DataFrame(matrix, index=ZONE_LABELS, columns=ZONE_LABELS)
