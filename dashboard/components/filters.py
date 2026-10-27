"""Criteria filters for charts.

An empty selection keeps every value. Filters only choose which stored rows
are drawn; they do not change aggregation rules or model outputs.
"""
from __future__ import annotations

from typing import Optional, Sequence

import pandas as pd

# Column name -> control label. Only columns present in the frame are shown.
CRITERIA = (
    ("month", "Month"),
    ("date", "Date"),
    ("district", "District"),
    ("category", "Category"),
    ("commodity_id", "Commodity"),
    ("market_id", "Market"),
    ("currency", "Currency"),
    ("model", "Model"),
    ("split", "Split"),
    ("base", "Base"),
    ("task", "Task"),
)


def _is_time(df: pd.DataFrame, col: str) -> bool:
    if col in ("month", "date"):
        return True
    return pd.api.types.is_datetime64_any_dtype(df[col])


def _options(df: pd.DataFrame, col: str) -> list:
    if _is_time(df, col):
        stamps = pd.to_datetime(df[col], errors="coerce").dropna()
        return sorted(stamps.dt.strftime("%Y-%m").unique().tolist())
    values = df[col].dropna()
    if values.empty:
        return []
    if pd.api.types.is_numeric_dtype(values) and col not in ("model", "split", "task"):
        return []
    return sorted({str(v) for v in values.unique() if str(v).strip() and str(v).lower() != "undefined"})


def chart_filters(df: pd.DataFrame, key: str,
                  include: Optional[Sequence[str]] = None) -> pd.DataFrame:
    """Draw criteria controls and return the matching rows.

    `include` limits which criteria are offered. Empty selections match all rows.
    """
    import streamlit as st

    if df is None or df.empty:
        return df
    wanted = list(include) if include is not None else [col for col, _ in CRITERIA]
    labels = dict(CRITERIA)
    specs = []
    for col in wanted:
        if col not in df.columns:
            continue
        opts = _options(df, col)
        if len(opts) < 2:
            continue
        specs.append((col, labels.get(col, col.replace("_", " ").capitalize()), opts))
    if not specs:
        return df

    st.markdown('<div class="sec-sub">Chart filters — leave a field empty to include every value.</div>',
                unsafe_allow_html=True)
    picked = {}
    for start in range(0, len(specs), 4):
        batch = specs[start:start + 4]
        cols = st.columns(len(batch))
        for col_box, (col, label, opts) in zip(cols, batch):
            picked[col] = col_box.multiselect(label, opts, key=f"cf_{key}_{col}")
    if st.button("Reset chart filters", key=f"cf_{key}_reset"):
        for col, _, _ in specs:
            st.session_state.pop(f"cf_{key}_{col}", None)
        st.rerun()

    out = df
    for col, sel in picked.items():
        if not sel:
            continue
        if _is_time(df, col):
            stamp = pd.to_datetime(out[col], errors="coerce").dt.strftime("%Y-%m")
            out = out[stamp.isin(sel)]
        else:
            out = out[out[col].astype(str).isin(sel)]
    st.caption(f"{len(out):,} of {len(df):,} rows match these filters.")
    return out


def has_rows(df: pd.DataFrame) -> bool:
    return df is not None and not df.empty
