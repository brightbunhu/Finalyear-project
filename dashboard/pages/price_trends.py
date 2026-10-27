"""Price Trends — investigate food-price movements without mixing incompatible series."""
from __future__ import annotations

import numpy as np
import streamlit as st

from components import layout as L
from components import charts as C
from utils import loaders as D
from utils import formatting as F

BASES = {
    "USD (converted)": ("usdprice", "usdprice", "USD"),
    "Nominal (within currency)": ("nominal_within_currency", "price", "local"),
}


def render() -> None:
    L.page_header("Price Trends",
                  "Explore price movements over time by category, commodity, district and market.",
                  provenance="Read from data_processed/panel_*.parquet. Series are never pooled across bases.")

    base_label = st.selectbox("Price base", list(BASES), key="pt_base")
    base, value_col, cur_hint = BASES[base_label]
    df = D.load_panel(base)
    if df.empty:
        L.unavailable(f"the {base} panel", f"data_processed/panel_{base}.parquet")
        return
    df = df.copy()

    # filters
    f = st.container()
    c1, c2, c3 = f.columns(3)
    months = sorted(df["month"].dt.strftime("%Y-%m").unique())
    dflt = months[-12:] if len(months) > 12 else months
    date_sel = c1.multiselect("Months", months, default=dflt, key="pt_months")
    cats = sorted(df["category"].dropna().unique()) if "category" in df.columns else []
    cat_sel = c2.multiselect("Category", cats, key="pt_cat")
    dists = sorted(df["district"].dropna().unique()) if "district" in df.columns else []
    dist_sel = c3.multiselect("District", dists, key="pt_dist")
    c4, c5, c6 = st.columns(3)
    comms = sorted(df["commodity_id"].dropna().unique()) if "commodity_id" in df.columns else []
    comm_sel = c4.multiselect("Commodity", comms, key="pt_comm")
    mkts = sorted(df["market_id"].dropna().unique()) if "market_id" in df.columns else []
    mkt_sel = c5.multiselect("Market", mkts, key="pt_mkt")
    agg = c6.selectbox("Aggregation", ["median", "mean"], key="pt_agg")
    if st.button("Reset filters", key="pt_reset"):
        for k in ("pt_months", "pt_cat", "pt_dist", "pt_comm", "pt_mkt"):
            st.session_state.pop(k, None)
        st.rerun()

    sub = df.copy()
    if date_sel:
        sub = sub[sub["month"].dt.strftime("%Y-%m").isin(date_sel)]
    if cat_sel:
        sub = sub[sub["category"].isin(cat_sel)]
    if dist_sel:
        sub = sub[sub["district"].isin(dist_sel)]
    if comm_sel:
        sub = sub[sub["commodity_id"].isin(comm_sel)]
    if mkt_sel:
        sub = sub[sub["market_id"].isin(mkt_sel)]

    unit = "USD / unit" if base == "usdprice" else "local currency / unit"
    st.caption(f"{F.intc(len(sub))} of {F.intc(len(df))} rows match the filters · "
               f"unit: {unit} · aggregation: {agg} · base: {base_label}")

    if sub.empty:
        st.info("No rows match the current filters. Widen the selection.")
        return

    tabs = st.tabs(["By category", "By commodity", "By district/market", "Distribution",
                    "Month-over-month", "Indexed", "Data"])

    agg_fn = "median" if agg == "median" else "mean"

    with tabs[0]:
        L.section("Monthly price by category", f"{agg.title()} {unit}.")
        g = sub.groupby(["month", "category"])[value_col].agg(agg_fn).reset_index()
        if not g.empty:
            C.show(C.multi_line(g, "month", value_col, "category",
                                y_title=unit, height=360))
        L.provenance_caption(f"panel_{base}.parquet · column {value_col}")

    with tabs[1]:
        L.section("Price by commodity", f"Top commodities, {agg} {unit}.")
        top_comms = sub["commodity_id"].value_counts().head(8).index
        g = sub[sub["commodity_id"].isin(top_comms)].groupby(
            ["month", "commodity_id"])[value_col].agg(agg_fn).reset_index()
        if not g.empty:
            C.show(C.multi_line(g, "month", value_col, "commodity_id",
                                y_title=unit, height=360))

    with tabs[2]:
        L.section("Price by district or market", f"{agg.title()} {unit}.")
        by = st.radio("Group by", ["district", "market_id"], horizontal=True, key="pt_by")
        if by in sub.columns:
            top = sub[by].value_counts().head(8).index
            g = sub[sub[by].isin(top)].groupby(["month", by])[value_col].agg(agg_fn).reset_index()
            if not g.empty:
                C.show(C.multi_line(g, "month", value_col, by, y_title=unit, height=360))

    with tabs[3]:
        L.section("Price distribution by category", "Box plots of filtered observations.")
        col = "category" if cat_sel or "category" in sub.columns else None
        if col and sub[col].nunique() > 1:
            C.show(C.box_by_group(sub.dropna(subset=[col]), col, value_col, height=380))
        else:
            C.show(C.histogram(sub[value_col].dropna(), bins=40, x_title=unit, height=340))
        st.caption("Box-plot outliers are statistical flags, not automatically data errors. "
                   "No values are removed.")

    with tabs[4]:
        L.section("Month-over-month change", f"Absolute change in {agg} {unit}.")
        g = sub.groupby("month")[value_col].agg(agg_fn).sort_index()
        d = g.diff().dropna()
        dd = d.reset_index(name="change")
        if not dd.empty:
            C.show(C.bar(dd, "month", "change", y_title=f"Δ {unit}", height=320))
        st.caption("Percentage change is shown only when the base level is strictly positive.")

    with tabs[5]:
        L.section("Indexed series", "Rebased to the first selected month (=100).")
        g = sub.groupby(["month", "category"])[value_col].agg(agg_fn).reset_index()
        if not g.empty:
            base_month = g["month"].min()
            base_vals = g[g["month"] == base_month].set_index("category")[value_col]
            g["index"] = g.apply(
                lambda r: 100 * r[value_col] / base_vals.get(r["category"], np.nan)
                if base_vals.get(r["category"], 0) else np.nan, axis=1)
            C.show(C.multi_line(g.dropna(subset=["index"]), "month", "index", "category",
                                y_title="Index (base month = 100)", height=360))
            st.caption(f"Base month: {base_month:%Y-%m}. Index requires a positive base level.")

    with tabs[6]:
        L.section("Filtered observations", "The exact rows behind the charts.")
        show = [c for c in ["month", "commodity_id", "district", "market_id", "category",
                            "currency", value_col] if c in sub.columns]
        st.dataframe(sub[show].head(1000), use_container_width=True, hide_index=True)
        st.download_button("Download filtered rows (CSV)",
                           sub[show].to_csv(index=False).encode("utf-8"),
                           file_name=f"price_trends_{base}.csv")
        st.caption(f"Up to 1,000 of {F.intc(len(sub))} rows are shown; the download is the "
                   "full filtered set.")

    st.info("No series are interpolated across missing months. Nominal prices from different "
            "currencies are never combined on one axis.")
    st.caption(f"Note: {L.DISCLAIMER}")
