"""Coverage & Quality — data coverage, missingness, temporal gaps and labelability."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from components import layout as L
from components import charts as C
from components import filters as CF
from utils import loaders as D
from utils import statistics as S
from utils import formatting as F


def _coverage_by(df: pd.DataFrame, col: str, top: int = 15) -> pd.DataFrame:
    if col not in df.columns:
        return pd.DataFrame()
    vc = df[col].value_counts(dropna=False).head(top).rename_axis(col).reset_index(name="rows")
    return vc


def render() -> None:
    L.page_header("Coverage & Quality",
                  "Coverage over time, currency and category mix, missingness and labelability.",
                  provenance="Computed from data_processed/panel_usdprice.parquet and the build log.")
    df = D.load_panel("usdprice")
    if df.empty:
        L.unavailable("the panel", "data_processed/panel_usdprice.parquet",
                      "Run the pipeline scripts first.")
        return

    n_dist = df["district"].nunique()
    lab1 = df["labelable_y1"].mean() if "labelable_y1" in df.columns else None
    lab2 = df["labelable_y2"].mean() if "labelable_y2" in df.columns else None
    miss = df.isna().mean().mean()

    L.kpi_row([
        {"icon": "▤", "color": "#EFF6FF", "label": "Total records",
         "value": F.intc(len(df)), "caption": "Food cells in the panel"},
        {"icon": "🏪", "color": "#F0FDF4", "label": "Unique markets",
         "value": F.intc(df["market_id"].nunique()), "caption": "distinct market_id"},
        {"icon": "🌽", "color": "#FEF9C3", "label": "Unique commodities",
         "value": F.intc(df["commodity_id"].nunique()), "caption": "distinct commodity_id"},
        {"icon": "🗺️", "color": "#FDF2F8", "label": "District coverage",
         "value": F.intc(n_dist), "caption": "distinct district"},
    ])
    st.write("")
    L.kpi_row([
        {"icon": "📅", "color": "#F5F3FF", "label": "Date coverage",
         "value": F.date_range(df["month"]), "caption": "min → max month"},
        {"icon": "🎯", "color": "#EFF6FF", "label": "Y1 labelable",
         "value": F.pct(lab1), "caption": "share with a next-month label"},
        {"icon": "🎯", "color": "#F0FDF4", "label": "Y2 labelable",
         "value": F.pct(lab2), "caption": "share with a next-month peer label"},
        {"icon": "❓", "color": "#FEF9C3", "label": "Mean missing rate",
         "value": F.pct(miss), "caption": "across all columns"},
    ])
    st.write("")

    L.section("Chart filters", "Summary cards above use the full panel. Charts use the filtered rows.")
    charts = CF.chart_filters(df, "coverage")

    tabs = st.tabs(["Coverage over time", "Mix", "Missingness", "Labelability", "Quality table"])

    with tabs[0]:
        L.section("Monthly record coverage", "Number of food cells per month.")
        if charts.empty:
            st.info("No rows match the chart filters.")
        else:
            mc = charts.groupby("month").size().reset_index(name="rows")
            C.show(C.line(mc, "month", "rows", y_title="Rows", height=300))
            st.caption(f"{len(mc)} months observed; median {F.intc(mc['rows'].median())} rows/month. "
                       f"Gaps in the line indicate months with no observations (not interpolated).")

    with tabs[1]:
        c1, c2 = st.columns(2)
        with c1:
            L.section("Coverage by currency")
            cur = _coverage_by(charts, "currency")
            if not cur.empty:
                C.show(C.bar(cur, "currency", "rows", x_title="Rows", height=280))
        with c2:
            L.section("Coverage by category")
            cat = _coverage_by(charts, "category")
            if not cat.empty:
                C.show(C.bar(cat, "category", "rows", x_title="Rows", height=280))
        st.write("")
        L.section("Coverage by district (top 15)")
        dist = _coverage_by(charts, "district")
        if not dist.empty:
            C.show(C.bar(dist, "rows", "district", horizontal=True,
                         x_title="Rows", height=380))
        L.provenance_caption("data_processed/panel_usdprice.parquet")

    with tabs[2]:
        L.section("Missingness by column", "Share of null values per column (top 25).")
        mt = S.missing_table(charts).head(25)
        if not mt.empty:
            C.show(C.bar(mt, "missing_pct", "variable", horizontal=True,
                         x_title="Missing (%)", height=max(320, 20 * len(mt))))
        with st.expander("Full missingness table"):
            st.dataframe(S.missing_table(charts), use_container_width=True, hide_index=True)

    with tabs[3]:
        L.section("Target labelability by month",
                  "Share of cells with a usable next-month label.")
        if charts.empty:
            st.info("No rows match the chart filters.")
        elif "labelable_y1" in charts.columns and "labelable_y2" in charts.columns:
            lab = charts.groupby("month")[["labelable_y1", "labelable_y2"]].mean().reset_index()
            lab_long = lab.melt("month", var_name="target", value_name="labelable")
            C.show(C.multi_line(lab_long, "month", "labelable", "target",
                                y_title="Share labelable", height=320))
            st.caption("Labelability falls in later months because the next month is "
                       "unobserved. Cells are not imputed.")
        else:
            L.unavailable("labelability columns", "labelable_y1 / labelable_y2")

    with tabs[4]:
        L.section("Field quality table",
                  "Missingness, distinct counts, range and a named quality rule.")
        rows = []
        for c in df.columns:
            s = df[c]
            rng = ""
            if pd.api.types.is_numeric_dtype(s):
                rng = f"{F.num(s.min())} … {F.num(s.max())}"
            rule = ""
            flag = ""
            if c in ("price", "usdprice"):
                rule = "Must be > 0"
                flag = F.intc(int((s <= 0).sum()))
            elif c == "rain_anom_z":
                rule = "|z| reported, not clipped"
                flag = "—"
            elif c == "peer_count":
                rule = "≥ 1 for a valid peer median"
                flag = F.intc(int((s.fillna(0) < 1).sum()))
            rows.append({
                "Field": c, "Missing": F.intc(s.isna().sum()),
                "Missing %": F.num(100 * s.isna().mean(), 2),
                "Distinct": F.intc(s.nunique(dropna=True)),
                "Type": str(s.dtype), "Range": rng or "—",
                "Quality rule": rule or "—", "Flagged": flag or "—",
                "Severity": ("serious" if (c in ("price", "usdprice") and
                             pd.api.types.is_numeric_dtype(s) and (s <= 0).any())
                             else ("info" if rule else "")),
            })
        q = pd.DataFrame(rows)
        st.dataframe(q, use_container_width=True, hide_index=True)
        st.download_button("Download quality table (CSV)", q.to_csv(index=False).encode("utf-8"),
                           file_name="coverage_quality_table.csv")

    st.write("")
    L.section("Documented data-quality notes", "From reports/phase1_data_quality_report.md.")
    st.warning(
        "- A small number of markets lack coordinates and cannot be mapped.\n\n"
        "- `usdprice` contains implausibly small values (min ~1.5e-5); flagged, not removed.\n\n"
        "- `priceflag=aggregate` rows are retained (a documented decision).\n\n"
        "- Median series length is short, so only a minority of cells are next-month labelable.")
    st.caption(f"Note: {L.DISCLAIMER}")
