"""Geographic Explorer — spatial variation in stress, model scores, rainfall and coverage."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

from components import layout as L
from components import charts as C
from utils import loaders as D
from utils import formatting as F

PCOL = "p_hist_gradient_boosting"

COMMODITY_MAP = {
    51: "Maize (grain)",
    264: "Maize meal (roller)",
    96: "Oil (vegetable)",
    432: "Beans (sugar)",
    50: "Beans (general)",
    52: "Rice",
    185: "Salt",
    97: "Sugar",
    887: "Fish (kapenta)",
    119: "Groundnuts",
}


def render() -> None:
    L.page_header(
        "Geographic Explorer",
        "Interactive spatial map of model-predicted food-price stress and district-level risk across Zimbabwe.",
        provenance="artifacts/preds_*.parquet, data_processed/panel_usdprice.parquet, raw/geo/zwe_adm2_geoboundaries.geojson"
    )

    geo = D.load_geo(2)
    preds_y2_usd = D.load_preds("T2_usd_y2")
    preds_y1_usd = D.load_preds("T1_usd_y1")
    preds_y2_nom = D.load_preds("T4_nominal_y2")
    preds_y1_nom = D.load_preds("T3_nominal_y1")
    panel = D.load_panel("usdprice")

    # Filter controls in a clean card surface
    with st.container():
        f1, f2, f3, f4, f5, f6 = st.columns([1.1, 0.7, 1.0, 1.0, 1.0, 1.0])

        target_opt = f1.selectbox(
            "Prediction target",
            ["Y2: Spatial Price Stress (SPI ≥ 1.20)", "Y1: Return Surge (≥ 1.0σ)"],
            key="geo_target"
        )
        curr_opt = f2.selectbox("Currency", ["USD", "Nominal"], key="geo_currency")

        if curr_opt == "USD":
            df_active = preds_y2_usd if target_opt.startswith("Y2") else preds_y1_usd
            task_name = "T2_usd_y2" if target_opt.startswith("Y2") else "T1_usd_y1"
            ycol = "y2" if target_opt.startswith("Y2") else "y1"
            prev_base = 0.163 if target_opt.startswith("Y2") else 0.150
        else:
            df_active = preds_y2_nom if target_opt.startswith("Y2") else preds_y1_nom
            task_name = "T4_nominal_y2" if target_opt.startswith("Y2") else "T3_nominal_y1"
            ycol = "y2" if target_opt.startswith("Y2") else "y1"
            prev_base = 0.160 if target_opt.startswith("Y2") else 0.150

        if df_active.empty:
            L.unavailable("the prediction dataset for this selection", f"artifacts/preds_{task_name}.parquet")
            return

        avail_cids = sorted(df_active["commodity_id"].dropna().unique()) if "commodity_id" in df_active.columns else []
        comm_choices = ["All commodities"] + [COMMODITY_MAP.get(c, f"Commodity #{c}") for c in avail_cids if c in COMMODITY_MAP]
        comm_sel = f3.selectbox("Commodity", comm_choices, key="geo_comm")

        risk_filter = f4.selectbox(
            "Risk level",
            ["All risk categories", "Very High Risk", "High Risk", "Medium Risk", "Low Risk"],
            key="geo_risk"
        )

        months_avail = sorted(df_active["month"].dt.strftime("%Y-%m").unique()) if "month" in df_active.columns else []
        date_sel = f5.selectbox("Observation month", ["All holdout months"] + months_avail, index=0, key="geo_date")

        dist_avail = ["All districts"] + sorted(df_active["district"].dropna().unique()) if "district" in df_active.columns else ["All districts"]
        dist_sel = f6.selectbox("District", dist_avail, index=0, key="geo_dist")

    # Apply filters
    sub = df_active.copy()
    if comm_sel != "All commodities":
        rev_map = {v: k for k, v in COMMODITY_MAP.items()}
        selected_cid = rev_map.get(comm_sel)
        if selected_cid and "commodity_id" in sub.columns:
            sub = sub[sub["commodity_id"] == selected_cid]

    if date_sel != "All holdout months" and "month" in sub.columns:
        sub = sub[sub["month"].dt.strftime("%Y-%m") == date_sel]

    if dist_sel != "All districts" and "district" in sub.columns:
        sub = sub[sub["district"] == dist_sel]

    if sub.empty:
        st.info("No prediction observations match the selected filters. Please expand your criteria.")
        return

    # Build district aggregation
    agg = sub.groupby("district").agg(
        prob=(PCOL, "mean"),
        obs=(ycol, "mean"),
        min_p=(PCOL, "min"),
        max_p=(PCOL, "max"),
        n_obs=(ycol, "size")
    ).reset_index()

    # Assign risk band and category
    def _get_band(p: float):
        if p >= max(prev_base * 2.2, prev_base + 0.20):
            return "Very High Risk", "high", 3
        if p >= max(prev_base * 1.5, prev_base + 0.10):
            return "High Risk", "high", 2
        if p >= prev_base:
            return "Medium Risk", "med", 1
        return "Low Risk", "ok", 0

    bands = [_get_band(p) for p in agg["prob"]]
    agg["risk_label"] = [b[0] for b in bands]
    agg["risk_class"] = [b[1] for b in bands]
    agg["risk_num"] = [b[2] for b in bands]

    # Risk level filtering for district list
    filtered_agg = agg.copy()
    if risk_filter != "All risk categories":
        filtered_agg = filtered_agg[filtered_agg["risk_label"] == risk_filter]

    st.caption(f"Showing {len(agg)} administrative districts from {len(sub):,} scored market observations · Target: {task_name}")

    # Main 2/3 and 1/3 layout
    map_col, summary_col = st.columns([2.0, 1.0], gap="medium")

    # LEFT: Large interactive map (2/3 width)
    with map_col:
        L.section("Spatial Risk Distribution Map", "District-level food-price stress classifications with OpenStreetMap basemap.")
        if geo is None:
            L.unavailable("the district boundary file", "data_processed/zwe_adm2_simplified.geojson")
        else:
            # Build full 91-district dataset so the entire country is visible
            geo_districts = sorted({f["properties"]["shapeName"] for f in geo["features"]})
            df_full = pd.DataFrame({"district": geo_districts})
            df_full = df_full.merge(agg, on="district", how="left")

            def _classify_district(row):
                if pd.isna(row["prob"]):
                    return "Unmonitored / Baseline", "neutral", -1
                return _get_band(row["prob"])

            full_res = [_classify_district(r) for _, r in df_full.iterrows()]
            df_full["risk_label"] = [r[0] for r in full_res]
            df_full["risk_class"] = [r[1] for r in full_res]
            df_full["risk_num"] = [r[2] for r in full_res]
            df_full["prob_pct"] = df_full["prob"].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else "Unmonitored")
            df_full["obs_pct"] = df_full["obs"].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else "Unmonitored")
            df_full["n_obs_str"] = df_full["n_obs"].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "0")

            map_mode = st.radio(
                "Map display layer",
                ["4-Level Risk Classification", "Continuous Stress Gradient (%)"],
                horizontal=True,
                key="geo_map_layer"
            )

            import plotly.express as px

            if map_mode == "4-Level Risk Classification":
                color_map = {
                    "Very High Risk": "#EF4444",
                    "High Risk": "#F97316",
                    "Medium Risk": "#F59E0B",
                    "Low Risk": "#10B981",
                    "Unmonitored / Baseline": "#CBD5E1",
                }
                map_fn = getattr(px, "choropleth_map", px.choropleth_mapbox)
                fig_map = map_fn(
                    df_full,
                    geojson=geo,
                    locations="district",
                    featureidkey="properties.shapeName",
                    color="risk_label",
                    color_discrete_map=color_map,
                    category_orders={"risk_label": ["Very High Risk", "High Risk", "Medium Risk", "Low Risk", "Unmonitored / Baseline"]},
                    center=dict(lat=-19.0154, lon=29.1549),
                    zoom=5.4,
                    opacity=0.72,
                    hover_name="district",
                    hover_data={
                        "risk_label": True,
                        "prob_pct": True,
                        "obs_pct": True,
                        "n_obs_str": True,
                        "district": False,
                    },
                    labels={
                        "risk_label": "Classification",
                        "prob_pct": "Predicted Stress",
                        "obs_pct": "Observed Rate",
                        "n_obs_str": "Scored Observations",
                    }
                )
            else:
                map_fn = getattr(px, "choropleth_map", px.choropleth_mapbox)
                fig_map = map_fn(
                    df_full,
                    geojson=geo,
                    locations="district",
                    featureidkey="properties.shapeName",
                    color="prob",
                    color_continuous_scale="YlOrRd",
                    range_color=(0.0, 1.0),
                    center=dict(lat=-19.0154, lon=29.1549),
                    zoom=5.4,
                    opacity=0.72,
                    hover_name="district",
                    hover_data={
                        "risk_label": True,
                        "prob_pct": True,
                        "obs_pct": True,
                        "n_obs_str": True,
                        "prob": False,
                    },
                    labels={
                        "prob": "Predicted Probability",
                        "risk_label": "Classification",
                        "prob_pct": "Predicted Stress",
                        "obs_pct": "Observed Rate",
                        "n_obs_str": "Scored Observations",
                    }
                )

            # Apply OpenStreetMap tile style
            if hasattr(fig_map.layout, "map"):
                fig_map.layout.map.style = "open-street-map"
            elif hasattr(fig_map.layout, "mapbox"):
                fig_map.layout.mapbox.style = "open-street-map"

            fig_map.update_layout(
                height=530,
                margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor="rgba(0,0,0,0)",
                legend=dict(
                    title=dict(text="Risk Classification", font=dict(size=11, color=L.THEME["main_text"])),
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="left",
                    x=0,
                    font=dict(size=11, color=L.THEME["secondary_text"]),
                    bgcolor="rgba(255,255,255,0.9)",
                    bordercolor=L.THEME["border"],
                    borderwidth=1,
                )
            )

            C.show(fig_map)
            st.caption(
                "Base tiles rendered via **OpenStreetMap** with complete Zimbabwe ADM-2 district boundaries. "
                "Unmonitored districts in this selection appear in neutral grey. "
                "Predictions represent model outputs from persisted research artefacts and do not constitute official IPC acute malnutrition classifications."
            )


    # RIGHT: District summary panel (1/3 width)
    with summary_col:
        L.section("District Summary Panel", "Breakdown by risk category.")

        # Counts by risk category
        counts = agg["risk_label"].value_counts()
        c_vh = counts.get("Very High Risk", 0)
        c_h = counts.get("High Risk", 0)
        c_m = counts.get("Medium Risk", 0)
        c_l = counts.get("Low Risk", 0)

        rc1, rc2 = st.columns(2)
        with rc1:
            st.markdown(
                f'<div class="card" style="border-left: 4px solid {L.THEME["risk_very_high"]}; padding:10px 12px; margin-bottom:8px;">'
                f'<div style="font-size:11px;color:var(--text-secondary);font-weight:600;">VERY HIGH RISK</div>'
                f'<div style="font-size:24px;font-weight:700;color:{L.THEME["risk_very_high"]}">{c_vh} <span style="font-size:12px;color:var(--text-secondary);font-weight:500;">districts</span></div>'
                f'</div>', unsafe_allow_html=True
            )
            st.markdown(
                f'<div class="card" style="border-left: 4px solid {L.THEME["risk_medium"]}; padding:10px 12px; margin-bottom:8px;">'
                f'<div style="font-size:11px;color:var(--text-secondary);font-weight:600;">MEDIUM RISK</div>'
                f'<div style="font-size:24px;font-weight:700;color:{L.THEME["risk_medium"]}">{c_m} <span style="font-size:12px;color:var(--text-secondary);font-weight:500;">districts</span></div>'
                f'</div>', unsafe_allow_html=True
            )
        with rc2:
            st.markdown(
                f'<div class="card" style="border-left: 4px solid {L.THEME["risk_high"]}; padding:10px 12px; margin-bottom:8px;">'
                f'<div style="font-size:11px;color:var(--text-secondary);font-weight:600;">HIGH RISK</div>'
                f'<div style="font-size:24px;font-weight:700;color:{L.THEME["risk_high"]}">{c_h} <span style="font-size:12px;color:var(--text-secondary);font-weight:500;">districts</span></div>'
                f'</div>', unsafe_allow_html=True
            )
            st.markdown(
                f'<div class="card" style="border-left: 4px solid {L.THEME["risk_low"]}; padding:10px 12px; margin-bottom:8px;">'
                f'<div style="font-size:11px;color:var(--text-secondary);font-weight:600;">LOW RISK</div>'
                f'<div style="font-size:24px;font-weight:700;color:{L.THEME["risk_low"]}">{c_l} <span style="font-size:12px;color:var(--text-secondary);font-weight:500;">districts</span></div>'
                f'</div>', unsafe_allow_html=True
            )

        st.markdown(f"**District Detail ({len(filtered_agg)} matching)**")
        ranked = filtered_agg.sort_values("prob", ascending=False).head(10)

        rows_html = ""
        for _, r in ranked.iterrows():
            badge_html = L.badge(r["risk_label"], r["risk_class"])
            rows_html += (
                f'<div class="stage" style="padding: 8px 4px;">'
                f'<div class="dot {r["risk_class"]}"></div>'
                f'<div style="flex:1;">'
                f'<div style="font-weight:600;font-size:13px;color:var(--navy);">{L.esc(r["district"])}</div>'
                f'<div style="font-size:11.5px;color:var(--text-secondary);margin-top:2px;">{badge_html} · {int(r["n_obs"])} obs</div>'
                f'</div>'
                f'<div style="font-size:14px;font-weight:700;color:var(--navy);text-align:right;">{r["prob"]:.1%}</div>'
                f'</div>'
            )
        st.markdown(rows_html or '<div class="metric-cap">No districts in this category.</div>', unsafe_allow_html=True)

    st.write("")

    # Detailed district data table
    L.section("Detailed District Metric Table", "Exportable aggregate table underlying the geographic explorer.")
    tbl = agg[["district", "risk_label", "prob", "obs", "n_obs"]].rename(
        columns={
            "district": "District",
            "risk_label": "Risk Classification",
            "prob": "Mean Predicted Stress Probability",
            "obs": "Observed Stress Rate",
            "n_obs": "Observations Count",
        }
    ).sort_values("Mean Predicted Stress Probability", ascending=False)

    tbl["Mean Predicted Stress Probability"] = tbl["Mean Predicted Stress Probability"].map(lambda x: f"{x:.1%}")
    tbl["Observed Stress Rate"] = tbl["Observed Stress Rate"].map(lambda x: f"{x:.1%}")

    st.dataframe(tbl, use_container_width=True, hide_index=True)

    st.download_button(
        "Download District Aggregates (CSV)",
        agg.to_csv(index=False).encode("utf-8"),
        file_name=f"geographic_district_summary_{task_name}.csv",
        mime="text/csv",
        key="geo_dl_csv"
    )
