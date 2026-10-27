"""Number/date formatting helpers shared across pages."""
from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd


def _is_missing(v) -> bool:
    if v is None:
        return True
    try:
        return bool(pd.isna(v))
    except (TypeError, ValueError):
        return False


def num(v, dec: int = 2, dash: str = "—") -> str:
    if _is_missing(v):
        return dash
    try:
        f = float(v)
    except (TypeError, ValueError):
        return str(v)
    if not np.isfinite(f):
        return dash
    return f"{f:,.{dec}f}"


def intc(v, dash: str = "—") -> str:
    if _is_missing(v):
        return dash
    try:
        return f"{int(round(float(v))):,}"
    except (TypeError, ValueError):
        return dash


def pct(v, dec: int = 1, dash: str = "—") -> str:
    if _is_missing(v):
        return dash
    try:
        f = float(v)
    except (TypeError, ValueError):
        return dash
    if not np.isfinite(f):
        return dash
    return f"{f * 100:.{dec}f}%"


def ratio(a, b, dec: int = 1, dash: str = "—") -> str:
    if _is_missing(a) or _is_missing(b) or float(b) == 0:
        return dash
    return f"{float(a) / float(b) * 100:.{dec}f}%"


def money(v, currency: str = "", dec: int = 2, dash: str = "—") -> str:
    s = num(v, dec, dash)
    if s == dash:
        return dash
    return f"{currency} {s}".strip()


def date_range(series: pd.Series) -> str:
    s = pd.to_datetime(series, errors="coerce").dropna()
    if s.empty:
        return "—"
    return f"{s.min():%Y-%m} → {s.max():%Y-%m}"


def month_label(v) -> str:
    try:
        return pd.Timestamp(v).strftime("%Y-%m")
    except (TypeError, ValueError):
        return "—"


def zscore(v, dec: int = 2, dash: str = "—") -> str:
    if _is_missing(v):
        return dash
    try:
        return f"{float(v):+.{dec}f}"
    except (TypeError, ValueError):
        return dash


def safe_div(a: Optional[float], b: Optional[float]) -> Optional[float]:
    if _is_missing(a) or _is_missing(b) or float(b) == 0:
        return None
    return float(a) / float(b)
