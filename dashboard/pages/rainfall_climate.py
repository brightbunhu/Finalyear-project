"""Rainfall & Climate — rainfall inputs, anomalies, climatology and lead–lag evidence.

This page exposes rainfall features, including z-anomalies, and shows the
rainfall–price lead/lag table. Causal claims are not made.
"""
from __future__ import annotations

import numpy as np
import streamlit as st

from components import layout as L
from components import charts as C
from components import filters as CF
from utils import loaders as D
from utils import formatting as F


def render() -> None:
    L.page_header("Rainfall & Climate",
                  "District rainfall, z-anomalies, climatology and the lead/lag association with returns.",
                  provenance="data_processed/rainfall_district_month_anom.parquet; reports/phase6_lead_lag.csv; climatology parquet")

    # data loads
    rain_anom = D.load_rainfall_anom()
    rain = D.load_rainfall()
    clim = D.load_climatology()
    panel = D.load_panel("usdprice")

    # summary metrics
    metrics = []
    metrics.append({"icon": "🌧️", "label": "Rainfall district-month obs",
                    "value": F.intc(len(rain_anom) if not rain_anom.empty else (len(rain) if not rain else None)),
                    "color": "#EFF6FF"})
    if not rain_anom.empty:
        metrics.append({"icon": "📅", "label": "Date range",
                        "value": F.date_range(rain_anom["month"])})
    if panel is not None and not panel.empty:
        metrics.append({"icon": "🗺️", "label": "Districts in panel",
                        "value": F.intc(panel["district"].nunique())})
    L.kpi_row(metrics)
    st.write("")

    tabs = st.tabs(["Anomalies", "Climatology", "Lead–lag", "District coverage", "Data tables"])

    with tabs[0]:
        L.section("District rainfall anomaly (z) over time",
                  "Mean district-month z-anomaly across available districts.")
        if not rain_anom.empty:
            view = CF.chart_filters(rain_anom, "rain_z")
            if view.empty:
                st.info("No rows match the chart filters.")
            else:
                by_m = view.groupby("month")["rainfall_anom_z"].mean().reset_index()
                C.show(C.line(by_m, "month", "rainfall_anom_z",
                              y_title="Mean rainfall anomaly z", height=340))
            st.caption("Anomalies are based on district/month climatology. Values are "
                       "not winsorised here.")
        else:
            L.unavailable("rainfall anomalies", "data_processed/rainfall_district_month_anom.parquet")

    with tabs[1]:
        L.section("Seasonal climatology", "Climatology baseline by district and calendar month.")
        if not clim.empty:
            view = CF.chart_filters(clim, "clim")
            if view.empty:
                st.info("No rows match the chart filters.")
            else:
                C.show(C.multi_line(view, "cal_month", "clim_mean_mm", "district",
                                    y_title="Climatological mean (mm)", height=360))
            st.caption(f"{F.intc(len(view))} district-month climatology entries.")
        else:
            L.unavailable("climatology", "data_processed/rainfall_climatology.parquet")

    with tabs[2]:
        L.section("Lead–lag: rainfall anomaly vs next-month return",
                  "Pearson/Spearman correlations between rainfall lag (months) and next-month return.")
        ll = D.load_report_csv("phase6_lead_lag.csv")
        if ll.empty:
            L.unavailable("lead–lag table", "reports/phase6_lead_lag.csv")
        else:
            st.dataframe(ll, use_container_width=True, hide_index=True)
            plotted = CF.chart_filters(ll, "leadlag")
            c1, c2 = st.columns(2)
            with c1:
                u = plotted[plotted["base"] == "usdprice"] if "base" in plotted.columns else plotted
                if not u.empty:
                    C.show(C.bar(u, "rain_lag_months", "pearson_r",
                                 y_title="Pearson r", height=280,
                                 title="USD base (returns vs rainfall lag)"))
            with c2:
                n = plotted[plotted["base"] == "nominal_within_currency"] if "base" in plotted.columns else plotted
                if not n.empty:
                    C.show(C.bar(n, "rain_lag_months", "pearson_r",
                                 y_title="Pearson r", height=280,
                                 title="Nominal within-currency"))
            st.caption("The correlation is weak (peak ~ -0.11/-0.12 at 1-month lead). "
                       "This is evidence of association, not causation.")
            st.info("Rainfall is treated as an indirect predictor; dashboard outputs "
                    "do not establish a causal relationship.")

    with tabs[3]:
        L.section("District coverage and missingness",
                  "How many rainfall observations are present by district.")
        if not rain_anom.empty:
            cov_src = CF.chart_filters(rain_anom, "rain_cov")
            if cov_src.empty:
                st.info("No rows match the chart filters.")
            else:
                cov = cov_src.groupby("district").agg(
                    obs=("rainfall_anom_z", "size"),
                    missing_z=("rainfall_anom_z", lambda s: int(s.isna().sum())),
                    missing_mm=("rainfall_mm", lambda s: int(s.isna().sum())),
                ).reset_index()
                cov["missing_z%"] = 100 * cov["missing_z"] / cov["obs"].replace(0, np.nan)
                cov = cov.sort_values("obs", ascending=False).head(30)
                C.show(C.bar(cov, "obs", "district", horizontal=True,
                             x_title="Obs", height=420))
                st.dataframe(cov, use_container_width=True, hide_index=True)
        else:
            L.unavailable("coverage table")

    with tabs[4]:
        c1, c2, c3 = st.columns(3)
        with c1:
            if not rain_anom.empty:
                st.markdown("**Anomalies sample**")
                st.dataframe(rain_anom.head(200), use_container_width=True, hide_index=True)
        with c2:
            if not rain.empty:
                st.markdown("**Rainfall monthly sample**")
                st.dataframe(rain.head(200), use_container_width=True, hide_index=True)
        with c3:
            if not clim.empty:
                st.markdown("**Climatology sample**")
                st.dataframe(clim.head(200), use_container_width=True, hide_index=True)
        st.download_button("Download anomalies (CSV)",
                           rain_anom.to_csv(index=False).encode("utf-8") if not rain_anom.empty else b"",
                           disabled=rain_anom.empty,
                           file_name="rainfall_district_month_anom.csv")

    st.caption(f"Note: {L.DISCLAIMER}")
