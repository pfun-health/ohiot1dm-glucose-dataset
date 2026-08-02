#!/usr/bin/env python
"""convert2pfun.py — convert OhioT1DM CSVs to pfun format and fit the CMA model.

Run from the repo root with uv, e.g.:

    uv run python scripts/convert2pfun.py --list
    uv run python scripts/convert2pfun.py --convert "Ohio Data/Ohio2018_processed/test/559-ws-testing_processed.csv"
    uv run python scripts/convert2pfun.py --fit --metrics --N 288 --n-steps 6

The pfun-cma-model package writes a log file to ``logs/`` relative to the CWD,
so the CLI ensures that directory exists before importing pfun.
"""

import argparse
import json
from pathlib import Path
from typing import Any

from ohiot1dm_glucose_dataset import (
    collect_predictions,
    convert_ohio_to_pfun,
    fit_patient,
    regression_metrics,
    unscale_glucose,
    zone_metrics,
)

_REPO_ROOT = Path(__file__).parents[1]
N_STEPS_AHEAD = 6


def _test_csv_paths() -> list[Path]:
    """Return every patient CSV found under ``Ohio Data/*/test/``, sorted."""
    return sorted(_REPO_ROOT.glob("Ohio Data/*/test/*.csv"))


def _resolve_paths(raw: list[str]) -> list[Path]:
    """Resolve CLI paths to CSV files (explicit files/dirs or all test CSVs)."""
    if not raw:
        return _test_csv_paths()
    paths: list[Path] = []
    for entry in raw:
        path = Path(entry)
        if path.is_dir():
            paths.extend(sorted(path.glob("*.csv")))
        else:
            paths.append(path)
    return paths


def _ensure_logs_dir() -> None:
    """Ensure pfun's logging directory exists (relative to the CWD).

    Creation may legitimately fail (a file named ``logs`` exists, or the CWD
    is read-only); the library import surfaces the real error with chaining,
    so the CLI should not crash up front on an unwritable ``logs/`` path.
    """
    try:
        Path("logs").mkdir(exist_ok=True)
    except OSError:
        pass


def _cmd_convert(args: argparse.Namespace, paths: list[Path]) -> None:
    """Convert each CSV to pfun format and write ``{stem}_pfun.csv`` files.

    One bad file must not abort the batch: each conversion is wrapped in its
    own try/except, failures are reported per file, and a summary line
    ``Wrote k of n file(s).`` is printed at the end.
    """
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    failed: list[str] = []
    for path in paths:
        try:
            formatted = convert_ohio_to_pfun(path, N=args.N)
        except Exception as exc:  # noqa: BLE001 - one bad file must not abort the batch
            failed.append(f"{path.name}: {exc}")
            continue
        out_path = outdir / f"{path.stem}_pfun.csv"
        formatted.to_csv(out_path, index=False)
        written.append(out_path)
    for message in failed:
        print(f"FAILED: {message}")
    print(f"Wrote {len(written)} of {len(paths)} file(s).")
    for out_path in written:
        print(f"  {out_path}")


def _fit_one(path: Path, args: argparse.Namespace) -> Any | None:
    """Fit one CSV, printing progress/failures; returns the result or None."""
    print(f"  Fitting CMA to {path.name} ...")
    try:
        return fit_patient(path, N=args.N)
    except Exception as exc:  # noqa: BLE001 - one bad file must not abort the batch
        print(f"  FAILED {path.name}: {exc}")
        return None


def _cmd_fit(args: argparse.Namespace, paths: list[Path]) -> dict[Path, Any]:
    """Fit CMA to every CSV and print residual + fitted parameters per file."""
    results: dict[Path, Any] = {}
    for path in paths:
        result = _fit_one(path, args)
        if result is not None:
            results[path] = result

    for path, result in results.items():
        residual = float(result.infodict["result"].fun)
        print(f"  {path.name}: residual = {residual:.6f}")
        print(f"    popt_named = {result.popt_named}")
    print(f"Successfully fitted CMA to {len(results)} files.")
    return results


def _cmd_metrics(results: dict[Path, Any], args: argparse.Namespace) -> None:
    """Print regression metrics and the glucose-zone confusion matrix."""
    if not results:
        print("No fitted files; skipping metrics.")
        return
    y_true, y_pred = collect_predictions(results, n_steps=args.n_steps)
    if len(y_true) == 0:
        print("No aligned (y_true, y_pred) pairs; skipping metrics.")
        return

    y_true_mgdl = unscale_glucose(y_true, "mgdl")
    y_pred_mgdl = unscale_glucose(y_pred, "mgdl")
    metrics = regression_metrics(y_true_mgdl, y_pred_mgdl)
    # Zone thresholds (70/180) are defined in mg/dL, so the confusion matrix
    # is always computed on mg/dL values.
    zone_matrix = zone_metrics(y_true_mgdl, y_pred_mgdl)

    if args.format == "json":
        payload = {
            "n_files": len(results),
            "n_steps": args.n_steps,
            "units": args.units,
            "regression_metrics": metrics,
            "zone_confusion_matrix": zone_matrix.to_dict(),
        }
        print(json.dumps(payload, indent=2, default=str))
        return

    print(
        f"Regression metrics (unscaled to mg/dL, "
        f"{args.n_steps}-step model-grid forecast):"
    )
    print(f"  {'metric':<6} {'value':>14}")
    print(f"  {'N':<6} {metrics['N']:>14.0f}")
    print(f"  {'RMSE':<6} {metrics['RMSE']:>14.3f} mg/dL")
    print(f"  {'MAE':<6} {metrics['MAE']:>14.3f} mg/dL")
    print(f"  {'MARD':<6} {metrics['MARD']:>14.4f}")
    print(f"  {'R²':<6} {metrics['R²']:>14.4f}")
    print("\nGlucose-zone confusion matrix in mg/dL (rows=true, cols=predicted):")
    print(zone_matrix.to_string())


def _positive_int(value: str) -> int:
    """Argparse type: require a positive integer."""
    try:
        parsed = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"must be an integer, got {value!r}") from None
    if parsed < 1:
        raise argparse.ArgumentTypeError(f"must be a positive integer, got {parsed}")
    return parsed


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="convert2pfun.py",
        description=(
            "Convert OhioT1DM CSVs to pfun format and fit the CMA model."
        ),
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all patient CSV paths under Ohio Data/*/test/.",
    )
    parser.add_argument(
        "--convert",
        nargs="*",
        default=None,
        metavar="PATH",
        help="Convert CSVs to pfun format (default: all test CSVs).",
    )
    parser.add_argument(
        "--fit",
        nargs="*",
        default=None,
        metavar="PATH",
        help="Fit the CMA model to CSVs (default: all test CSVs).",
    )
    parser.add_argument(
        "--metrics",
        action="store_true",
        help="After --fit, print regression + glucose-zone metrics.",
    )
    parser.add_argument(
        "--N",
        type=_positive_int,
        default=288,
        help="Number of model output samples (default: 288).",
    )
    parser.add_argument(
        "--units",
        choices=["mgdl"],
        default="mgdl",
        help=(
            "Glucose units for metrics (default: mgdl). The OhioT1DM pipeline "
            "fits in mgdl-normalized space, so only mgdl is supported."
        ),
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format for --metrics (default: text).",
    )
    parser.add_argument(
        "--outdir",
        default="converted",
        help="Output directory for --convert (default: converted).",
    )
    parser.add_argument(
        "--n-steps",
        type=_positive_int,
        default=N_STEPS_AHEAD,
        help=(
            "Forecast horizon in n_steps model-grid steps for --metrics "
            "(default: 6)."
        ),
    )
    parser.add_argument(
        "paths",
        nargs="*",
        metavar="PATH",
        help=(
            "Patient CSV paths (files or directories) to process; "
            "default: all test CSVs."
        ),
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.list:
        for path in _test_csv_paths():
            print(path)
        return

    if args.convert is None and args.fit is None and not args.metrics:
        parser.error("no action specified; use --list, --convert, or --fit")

    if args.metrics and args.fit is None:
        parser.error("--metrics requires --fit")

    if args.convert is not None:
        _ensure_logs_dir()
        _cmd_convert(
            args, _resolve_paths(list(args.convert) + list(args.paths))
        )

    if args.fit is not None or args.metrics:
        _ensure_logs_dir()
        results = _cmd_fit(
            args, _resolve_paths(list(args.fit or []) + list(args.paths))
        )
        if args.metrics:
            _cmd_metrics(results, args)


if __name__ == "__main__":
    main()
