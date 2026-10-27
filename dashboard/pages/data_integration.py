"""Data & Integration — show how raw sources flow to the model-ready panel and artefacts."""
from __future__ import annotations

import streamlit as st

from components import layout as L
from utils import loaders as D
from utils import formatting as F


def _status_dot(ok: bool) -> tuple[str, str]:
    return ("ok", "Available") if ok else ("na", "Not available")


def _pipeline_stages() -> list[dict]:
    raw_ok = all(p.exists() for *_, p, _ in D.SOURCES)
    cross = D.DATA_PROC / "market_admin_crosswalk.csv"
    rain = D.DATA_PROC / "rainfall_district_month_anom.parquet"
    panel_u = D.DATA_PROC / "panel_usdprice.parquet"
    panel_n = D.DATA_PROC / "panel_nominal_within_currency.parquet"
    preds = list(D.ART.glob("preds_*.parquet"))
    models = list(D.MODELS.glob("*.joblib"))
    return [
        {"name": "Raw sources", "paths": [p for *_, p, _ in D.SOURCES], "ok": raw_ok,
         "fields": "prices, markets, rainfall, boundaries, population",
         "purpose": "Validated source tables consumed by the build."},
        {"name": "Market–district crosswalk", "paths": [cross], "ok": cross.exists(),
         "fields": "market_id, district, latitude, longitude",
         "purpose": "Point-in-polygon matching to geoBoundaries districts."},
        {"name": "Rainfall & features", "paths": [rain], "ok": rain.exists(),
         "fields": "rainfall_mm, rainfall_anom_z, lags, rolling",
         "purpose": "District-month rainfall features and climatology anomalies."},
        {"name": "Model-ready panels", "paths": [panel_u, panel_n], "ok": panel_u.exists() and panel_n.exists(),
         "fields": "price features, targets y1/y2, labelability",
         "purpose": "Engineered features + labels on both price bases."},
        {"name": "Persisted models", "paths": models, "ok": bool(models),
         "fields": "Hist-GBM pipelines + metadata",
         "purpose": "Trained estimators used for scoring."},
        {"name": "Prediction artefacts", "paths": preds, "ok": bool(preds),
         "fields": "holdout scores per task/model",
         "purpose": "Historical holdout probabilities for inspection."},
    ]


def _preview_tabs() -> None:
    datasets = [
        ("WFP food prices", D.RAW / "wfp_food_prices_zwe.csv", "csv"),
        ("WFP markets", D.RAW / "wfp_markets_zwe.csv", "csv"),
        ("Crosswalk", D.DATA_PROC / "market_admin_crosswalk.csv", "csv"),
        ("Rainfall anomalies", D.DATA_PROC / "rainfall_district_month_anom.parquet", "parquet"),
        ("Panel (USD)", D.DATA_PROC / "panel_usdprice.parquet", "parquet"),
        ("Panel (nominal)", D.DATA_PROC / "panel_nominal_within_currency.parquet", "parquet"),
        ("Predictions T2", D.ART / "preds_T2_usd_y2.parquet", "parquet"),
        ("Climatology", D.DATA_PROC / "rainfall_climatology.parquet", "parquet"),
    ]
    found = [(n, p, k) for n, p, k in datasets if p.exists()]
    if not found:
        L.unavailable("dataset previews")
        return
    labels = [n for n, _, _ in found]
    choice = st.selectbox("Inspect a dataset", labels, key="di_preview")
    name, path, kind = next(f for f in found if f[0] == choice)
    df = D.load_parquet(path) if kind == "parquet" else D.load_csv(path)
    if df.empty:
        L.unavailable(name, str(path.relative_to(D.ROOT)))
        return
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", F.intc(len(df)))
    c2.metric("Columns", F.intc(df.shape[1]))
    c3.metric("Size (MB)", F.num(path.stat().st_size / 1e6, 2))
    dcols = [c for c in ("month", "date") if c in df.columns]
    c4.metric("Date range", F.date_range(df[dcols[0]]) if dcols else "—")

    L.provenance_caption(str(path.relative_to(D.ROOT)))
    show_cols = st.multiselect("Columns to display", list(df.columns),
                               default=list(df.columns)[: min(10, df.shape[1])],
                               key="di_cols")
    st.dataframe(df[show_cols].head(200) if show_cols else df.head(200),
                 use_container_width=True, hide_index=True)

    with st.expander("Missingness & duplicates"):
        miss = df.isna().mean().sort_values(ascending=False)
        miss = (miss[miss > 0] * 100).round(2)
        if miss.empty:
            st.caption("No missing values detected in this dataset.")
        else:
            st.caption("Missing percentage by column (top 15):")
            st.dataframe(miss.head(15).rename("missing_%").to_frame().T,
                         use_container_width=True)
        st.caption(f"Duplicate full rows: {int(df.duplicated().sum()):,}")


def _integration_metrics() -> None:
    panel = D.load_panel("usdprice")
    cross = D.load_crosswalk()
    rain = D.load_rainfall_anom()
    if panel.empty:
        L.unavailable("integration metrics", "data_processed/panel_usdprice.parquet")
        return
    raw_rows = D.build_log_raw_rows()
    n_markets = panel["market_id"].nunique()
    n_dist = panel["district"].nunique()
    matched = int(cross["district_geo"].notna().sum()) if (
        not cross.empty and "district_geo" in cross.columns) else None
    unmatched = int(cross["district_geo"].isna().sum()) if (
        not cross.empty and "district_geo" in cross.columns) else None
    labelable = int(panel["labelable_y2"].sum()) if "labelable_y2" in panel.columns else None
    rain_cov = panel["rain_anom_z"].notna().mean() if "rain_anom_z" in panel.columns else None
    coord = (panel["district"].notna().mean()) if "district" in panel.columns else None

    st.caption("All values are computed from the stored artefacts; denominators are stated.")
    L.kpi_row([
        {"icon": "▤", "label": "Price records integrated",
         "value": F.intc(raw_rows), "caption": "From panel_build_log.txt", "color": "#EFF6FF"},
        {"icon": "🧱", "label": "Monthly food cells",
         "value": F.intc(len(panel)), "caption": "Rows in the USD panel", "color": "#F0FDF4"},
        {"icon": "🏪", "label": "Markets matched",
         "value": F.intc(matched),
         "caption": f"{F.intc(unmatched)} unmatched of {F.intc(len(cross))}", "color": "#FEF9C3"},
        {"icon": "🎯", "label": "Y2-labelable cells",
         "value": F.ratio(labelable, len(panel)),
         "caption": f"{F.intc(labelable)} of {F.intc(len(panel))}", "color": "#FDF2F8"},
    ])
    rows = [
        {"Metric": "Markets in panel", "Value": F.intc(n_markets), "Denominator": "distinct market_id"},
        {"Metric": "Districts in panel", "Value": F.intc(n_dist), "Denominator": "distinct district"},
        {"Metric": "Rainfall district-month rows", "Value": F.intc(len(rain)), "Denominator": "rows"},
        {"Metric": "Model-ready rows (USD)", "Value": F.intc(len(panel)), "Denominator": "rows"},
        {"Metric": "Rainfall feature coverage", "Value": F.ratio(
            rain_cov is not None and rain_cov * len(panel), len(panel)),
         "Denominator": "non-null rain_anom_z"},
        {"Metric": "Coordinate (district) coverage", "Value": F.ratio(
            (coord or 0) * len(panel), len(panel)), "Denominator": "non-null district"},
        {"Metric": "Target-label coverage (Y2)", "Value": F.ratio(labelable, len(panel)),
         "Denominator": "labelable_y2"},
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)


def render() -> None:
    L.page_header("Data & Integration",
                  "Trace every dataset from raw source to the model-ready panel and predictions.",
                  provenance="Paths, counts and timestamps are read from the actual repository files.")

    L.section("Pipeline overview",
              "Each stage is inspected for existence and readability, not just filename presence.")
    stages = _pipeline_stages()
    cols = st.columns(3, gap="small")
    for i, s in enumerate(stages):
        dot, status = _status_dot(s["ok"])
        cls = "ok" if s["ok"] else "na"
        mid = ""
        for p in s["paths"][:3]:
            rel = p.relative_to(D.ROOT) if p.is_absolute() else p
            mid += f'<div class="metric-cap">• {L.esc(rel)}</div>'
        with cols[i % 3]:
            L.card(f'<div class="dot {dot}" style="display:inline-block"></div> '
                   f'<span class="stage-name">{i+1}. {L.esc(s["name"])}</span> '
                   f'{L.badge(status, cls)}'
                   f'<div class="stage-desc" style="margin-top:6px">{L.esc(s["purpose"])}</div>'
                   f'<div class="stage-desc">Fields: {L.esc(s["fields"])}</div>'
                   f'{mid}')
            st.write("")

    st.write("")
    L.section("Artefact catalogue", "Searchable inventory of pipeline artefacts.")
    cat = D.catalog_frame()
    if cat.empty:
        L.unavailable("the artefact catalogue")
    else:
        fc1, fc2 = st.columns([1, 1])
        stage_opts = sorted(cat["Stage"].unique())
        pick_stage = fc1.multiselect("Filter by stage", stage_opts)
        search = fc2.text_input("Search name / path / purpose", "")
        view = cat.copy()
        if pick_stage:
            view = view[view["Stage"].isin(pick_stage)]
        if search:
            mask = view.apply(lambda r: search.lower() in " ".join(
                r.astype(str)).lower(), axis=1)
            view = view[mask]
        st.caption(f"{len(view)} of {len(cat)} artefacts shown.")
        st.dataframe(view, use_container_width=True, hide_index=True)

    st.write("")
    L.section("Dataset previews", "Dimensions, date range, missingness and a small sample.")
    _preview_tabs()

    st.write("")
    L.section("Integration completeness", "Numerators and denominators from the real panel.")
    _integration_metrics()

    st.write("")
    L.section("Data lineage & caveats")
    st.markdown(
        "- Raw sources are validated before aggregation; the build log records raw price rows.\n"
        "- Market-to-district matching uses geoBoundaries ADM2 polygons; unmatched markets "
        "have no coordinates and are excluded from maps.\n"
        "- `priceflag=aggregate` rows are retained by design (documented as a decision).\n"
        "- Missing values are reported, never imputed, in the dashboard.")
    st.caption(f"Note: {L.DISCLAIMER}")
