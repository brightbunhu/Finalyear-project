"""Cached data access and artefact catalogue for the dashboard.

All loaders read genuine project artefacts only. Missing files return an empty
object (never a fabricated one); callers render an explicit unavailable state.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
DATA_PROC = ROOT / "data_processed"
ART = ROOT / "artifacts"
MODELS = ROOT / "models"
FIG = ROOT / "figures"
REP = ROOT / "reports"
RAW = ROOT / "raw"
CONFIG = ROOT / "config"


@st.cache_data(show_spinner=False)
def load_config() -> Dict[str, Any]:
    """Load config/targets.yml (single source of truth). Empty dict if missing."""
    p = CONFIG / "targets.yml"
    if not p.exists():
        return {}
    try:
        import yaml
        return yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}

TASKS = ["T1_usd_y1", "T2_usd_y2", "T3_nominal_y1", "T4_nominal_y2"]
TASK_META = {
    "T1_usd_y1": {"base": "usdprice", "target": "y1", "label": "USD · Y1 standardised-return stress"},
    "T2_usd_y2": {"base": "usdprice", "target": "y2", "label": "USD · Y2 peer-relative stress"},
    "T3_nominal_y1": {"base": "nominal_within_currency", "target": "y1", "label": "Nominal · Y1 standardised-return stress"},
    "T4_nominal_y2": {"base": "nominal_within_currency", "target": "y2", "label": "Nominal · Y2 peer-relative stress"},
}
MODEL_NAMES = {
    "y1_return_histgbm_usd": ("T1_usd_y1", "usdprice", "y1"),
    "y2_peer_histgbm_usd": ("T2_usd_y2", "usdprice", "y2"),
}


# --------------------------------------------------------------- primitives
@st.cache_data(show_spinner=False)
def _read_parquet(path_str: str, mtime: float) -> pd.DataFrame:
    df = pd.read_parquet(path_str)
    for c in ("month", "date"):
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")
    return df


@st.cache_data(show_spinner=False)
def _read_csv(path_str: str, mtime: float) -> pd.DataFrame:
    return pd.read_csv(path_str, low_memory=False)


def _maybe_datetime(df: pd.DataFrame) -> pd.DataFrame:
    for c in ("month", "date"):
        if c in df.columns and not pd.api.types.is_datetime64_any_dtype(df[c]):
            df[c] = pd.to_datetime(df[c], errors="coerce")
    return df


def load_parquet(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return _maybe_datetime(_read_parquet(str(path), path.stat().st_mtime))


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return _maybe_datetime(_read_csv(str(path), path.stat().st_mtime))


# --------------------------------------------------------------- datasets
def load_panel(base: str) -> pd.DataFrame:
    return load_parquet(DATA_PROC / f"panel_{base}.parquet")


def load_preds(task: str) -> pd.DataFrame:
    return load_parquet(ART / f"preds_{task}.parquet")


def load_metrics() -> pd.DataFrame:
    return load_csv(ART / "metrics_all_tasks.csv")


def load_markets() -> pd.DataFrame:
    return load_csv(RAW / "wfp_markets_zwe.csv")


def load_crosswalk() -> pd.DataFrame:
    return load_csv(DATA_PROC / "market_admin_crosswalk.csv")


def load_rainfall_anom() -> pd.DataFrame:
    return load_parquet(DATA_PROC / "rainfall_district_month_anom.parquet")


def load_rainfall() -> pd.DataFrame:
    return load_parquet(DATA_PROC / "rainfall_district_month.parquet")


def load_climatology() -> pd.DataFrame:
    return load_parquet(DATA_PROC / "rainfall_climatology.parquet")


@st.cache_data(show_spinner=False)
def load_geo(level: int = 2) -> Optional[dict]:
    p_sim = DATA_PROC / f"zwe_adm{level}_simplified.geojson"
    if p_sim.exists():
        return json.loads(p_sim.read_text(encoding="utf-8"))
    p = RAW / "geo" / f"zwe_adm{level}_geoboundaries.geojson"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


@st.cache_resource(show_spinner=False)
def load_model(name: str):
    """Return (estimator_pipeline, metadata_dict) or (None, None)."""
    meta_p = MODELS / f"{name}.meta.json"
    model_p = MODELS / f"{name}.joblib"
    if not (meta_p.exists() and model_p.exists()):
        return None, None
    try:
        import joblib
        return joblib.load(model_p), json.loads(meta_p.read_text(encoding="utf-8"))
    except Exception:
        return None, None


@st.cache_data(show_spinner=False)
def build_log_raw_rows() -> Optional[int]:
    p = DATA_PROC / "panel_build_log.txt"
    if not p.exists():
        return None
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.startswith("raw price rows:"):
            try:
                return int(line.split(":")[1].strip())
            except (IndexError, ValueError):
                return None
    return None


@st.cache_data(show_spinner=False)
def build_log_lines() -> List[str]:
    p = DATA_PROC / "panel_build_log.txt"
    return p.read_text(encoding="utf-8").splitlines() if p.exists() else []


# --------------------------------------------------------------- catalogue
# documented source datasets consumed by the research pipeline
SOURCES = [
    ("WFP food prices", "Raw source", RAW / "wfp_food_prices_zwe.csv",
     "Monthly market food prices (all categories)."),
    ("WFP markets", "Raw source", RAW / "wfp_markets_zwe.csv",
     "Market master list with admin hierarchy and coordinates."),
    ("CHIRPS rainfall", "Raw source", RAW / "yr.nc",
     "Gridded precipitation netCDF, aggregated to district-month."),
    ("geoBoundaries ADM1", "Raw source", RAW / "geo" / "zwe_adm1_geoboundaries.geojson",
     "Province polygons."),
    ("geoBoundaries ADM2", "Raw source", RAW / "geo" / "zwe_adm2_geoboundaries.geojson",
     "District polygons used for point-in-polygon matching."),
    ("HAPI population", "Raw source", RAW / "hdx_hapi_population_zwe.csv",
     "District population used for log_population."),
]

CATALOG = [
    ("WFP food prices", "Raw", RAW / "wfp_food_prices_zwe.csv", "Food-price source"),
    ("WFP markets", "Raw", RAW / "wfp_markets_zwe.csv", "Market coordinates"),
    ("CHIRPS rainfall (netCDF)", "Raw", RAW / "yr.nc", "Rainfall source"),
    ("HAPI population", "Raw", RAW / "hdx_hapi_population_zwe.csv", "Population"),
    ("Market–district crosswalk", "Merge", DATA_PROC / "market_admin_crosswalk.csv", "Geo matching"),
    ("Rainfall district-month", "Feature", DATA_PROC / "rainfall_district_month.parquet", "Rainfall features"),
    ("Rainfall anomalies", "Feature", DATA_PROC / "rainfall_district_month_anom.parquet", "Rainfall anomaly z-scores"),
    ("Rainfall climatology", "Feature", DATA_PROC / "rainfall_climatology.parquet", "Climatology baseline"),
    ("Panel (USD)", "Model-ready", DATA_PROC / "panel_usdprice.parquet", "USD price panel + features + labels"),
    ("Panel (nominal)", "Model-ready", DATA_PROC / "panel_nominal_within_currency.parquet", "Nominal panel + features + labels"),
    ("Metrics (all tasks)", "Evaluation", ART / "metrics_all_tasks.csv", "CV + holdout metrics"),
    ("Predictions T1", "Prediction", ART / "preds_T1_usd_y1.parquet", "Holdout scores"),
    ("Predictions T2", "Prediction", ART / "preds_T2_usd_y2.parquet", "Holdout scores"),
    ("Predictions T3", "Prediction", ART / "preds_T3_nominal_y1.parquet", "Holdout scores"),
    ("Predictions T4", "Prediction", ART / "preds_T4_nominal_y2.parquet", "Holdout scores"),
    ("Optuna summary", "Evaluation", ART / "optuna_summary.csv", "Tuning results"),
    ("Run metadata", "Metadata", ART / "run_metadata.json", "Run configuration"),
    ("Model Y1 metadata", "Model", MODELS / "y1_return_histgbm_usd.meta.json", "Persisted model card"),
    ("Model Y2 metadata", "Model", MODELS / "y2_peer_histgbm_usd.meta.json", "Persisted model card"),
]


def _file_meta(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"exists": False, "size_mb": None, "modified": None,
                "rows": None, "cols": None, "date_range": None, "format": path.suffix.lstrip(".")}
    st_ = path.stat()
    info: Dict[str, Any] = {
        "exists": True,
        "size_mb": round(st_.st_size / 1e6, 2),
        "modified": datetime.fromtimestamp(st_.st_mtime).strftime("%Y-%m-%d %H:%M"),
        "format": path.suffix.lstrip(".").upper() or "FILE",
        "rows": None, "cols": None, "date_range": None,
    }
    try:
        if path.suffix == ".parquet":
            import pyarrow.parquet as pq
            md = pq.ParquetFile(path).metadata
            info["rows"] = md.num_rows
            info["cols"] = md.num_columns
            df = pd.read_parquet(path, columns=None)
            for c in ("month", "date"):
                if c in df.columns:
                    d = pd.to_datetime(df[c], errors="coerce")
                    info["date_range"] = f"{d.min():%Y-%m} → {d.max():%Y-%m}"
                    break
        elif path.suffix == ".csv":
            df = pd.read_csv(path, low_memory=False)
            info["rows"], info["cols"] = df.shape
            for c in ("month", "date"):
                if c in df.columns:
                    d = pd.to_datetime(df[c], errors="coerce")
                    info["date_range"] = f"{d.min():%Y-%m} → {d.max():%Y-%m}"
                    break
    except Exception:
        pass
    return info


# --------------------------------------------------------------- reports/artefacts
def load_report_csv(name: str) -> pd.DataFrame:
    return load_csv(REP / name)


def load_artifact_csv(name: str) -> pd.DataFrame:
    return load_csv(ART / name)


@st.cache_data(show_spinner=False)
def load_artifact_json(name: str) -> Optional[dict]:
    p = ART / name
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def fig_path(name: str) -> Optional[Path]:
    p = FIG / name
    return p if p.exists() else None


def report_path(name: str) -> Optional[Path]:
    p = REP / name
    return p if p.exists() else None


@st.cache_data(show_spinner=False)
def read_text(name: str) -> Optional[str]:
    p = REP / name
    if not p.exists():
        return None
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None


# named figures confirmed present in figures/ (used for evidence galleries)
FIGURES = {
    "coverage_monthly": "fig4.3.1_monthly_coverage.png",
    "class_balance": "fig4.3.2_class_balance.png",
    "prev_by_category": "fig4.3.3_prev_by_category.png",
    "median_usd_price": "fig4.3.4_median_usd_price.png",
    "median_nominal_price": "fig4.3.5_median_nominal_price.png",
    "rain_anom_dist": "fig4.3.6_rainfall_anomaly_dist.png",
    "rain_anom_series": "fig4.3.7_rainfall_anomaly_series.png",
    "returns_dist": "fig4.3.8_returns_distribution.png",
    "missingness": "fig4.3.9_missingness.png",
    "roc_T1": "fig4.4.1.5_roc_T1_usd_y1.png",
    "roc_T2": "fig4.4.1.6_roc_T2_usd_y2.png",
    "roc_T3": "fig4.4.1.7_roc_T3_nominal_y1.png",
    "roc_T4": "fig4.4.1.8_roc_T4_nominal_y2.png",
    "pr_T1": "fig4.4.1.9_pr_T1_usd_y1.png",
    "pr_T2": "fig4.4.1.10_pr_T2_usd_y2.png",
    "pr_T3": "fig4.4.1.11_pr_T3_nominal_y1.png",
    "pr_T4": "fig4.4.1.12_pr_T4_nominal_y2.png",
    "cv_holdout_T1": "fig4.4.1.1_cv_vs_holdout_T1_usd_y1.png",
    "cv_holdout_T2": "fig4.4.1.2_cv_vs_holdout_T2_usd_y2.png",
    "bootstrap_ci": "fig4.4.2.1_bootstrap_ci.png",
    "confusion_T1": "fig4.4.3.1_confusion_T1_usd_y1.png",
    "confusion_T2": "fig4.4.3.2_confusion_T2_usd_y2.png",
    "calibration_T1": "fig4.4.4.1_calibration_T1_usd_y1.png",
    "calibration_T2": "fig4.4.4.2_calibration_T2_usd_y2.png",
    "lead_lag": "fig4.5.1_lead_lag.png",
    "importance_T1": "fig4.6.1_importance_T1_usd_y1.png",
    "importance_T2": "fig4.6.2_importance_T2_usd_y2.png",
    "threshold_prevalence": "fig4.7.1_threshold_prevalence.png",
    "y2_diagnostics": "phase7_y2_diagnostics.png",
}


@st.cache_data(show_spinner=False)
def load_folds(task: str) -> dict:
    return load_artifact_json(f"folds_{task}.json") or {}


@st.cache_data(show_spinner=False)
def load_optuna_summary() -> pd.DataFrame:
    return load_artifact_csv("optuna_summary.csv")


@st.cache_data(show_spinner=False)
def load_run_metadata() -> dict:
    return load_artifact_json("run_metadata.json") or {}


@st.cache_data(show_spinner=False)
def load_perm_importance(task: str) -> pd.DataFrame:
    """Permutation importance for a task; empty frame if absent or empty file."""
    p = ART / f"perm_importance_{task}.csv"
    if not p.exists() or p.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(p)
    except Exception:
        return pd.DataFrame()


@st.cache_data(show_spinner=False)
def catalog_frame() -> pd.DataFrame:
    rows = []
    for name, stage, path, purpose in CATALOG:
        m = _file_meta(path)
        rows.append({
            "Artefact": name,
            "Stage": stage,
            "Path": str(path.relative_to(ROOT)),
            "Format": m["format"],
            "Rows": str(m["rows"]) if m["rows"] is not None else "—",
            "Columns": str(m["cols"]) if m["cols"] is not None else "—",
            "Date range": m["date_range"] or "—",
            "Size (MB)": m["size_mb"] if m["size_mb"] is not None else "—",
            "Modified": m["modified"] or "—",
            "Status": "Available" if m["exists"] else "Not available",
            "Purpose": purpose,
        })
    return pd.DataFrame(rows)
