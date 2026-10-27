"""Historical Holdout Predictions — inspect saved out-of-sample scores (not live forecasts)."""
from __future__ import annotations

import numpy as np
import streamlit as st

from components import layout as L
from components import charts as C
from utils import loaders as D
from utils import formatting as F

MODEL_LABELS = {
    "p_majority": "Majority baseline",
    "p_persistence": "Persistence baseline",
    "p_logistic_elasticnet": "Logistic (elastic net)",
    "p_hist_gradient_boosting": "Hist gradient boosting",
    "p_xgboost": "XGBoost",
}


def render() -> None:
    L.page_header("Historical Holdout Predictions",
                  "Ranked out-of-sample scores from the stored artefacts.",
                  provenance="artifacts/preds_T{1..4}_*.parquet")
    st.error("Historical holdout predictions — not live forecasts. These scores were "
             "produced on a past, fixed holdout window.")

    task = st.selectbox("Task", D.TASKS, key="hh_task")
    df = D.load_preds(task)
    if df.empty:
        L.unavailable(f"predictions for {task}", f"artifacts/preds_{task}.parquet",
                      "See the Model Performance page for evaluation evidence.")
        return
    ycol = "y1" if "y1" in df.columns else "y2"
    pcols = [c for c in df.columns if c.startswith("p_")]
    model_col = st.selectbox("Model", pcols, index=pcols.index("p_hist_gradient_boosting")
                             if "p_hist_gradient_boosting" in pcols else 0,
                             format_func=lambda c: MODEL_LABELS.get(c, c), key="hh_model")

    # filters
    c1, c2, c3 = st.columns(3)
    months = sorted(df["month"].dt.strftime("%Y-%m").unique())
    msel = c1.multiselect("Month", months, key="hh_months")
    dsel = c2.multiselect("District", sorted(df["district"].dropna().unique()), key="hh_dist")
    cat = sorted(df["category"].dropna().astype(str).unique()) if "category" in df.columns else []
    csel = c3.multiselect("Category", cat, key="hh_cat")
    c4, c5, c6 = st.columns(3)
    comms = sorted(df["commodity_id"].dropna().astype(str).unique()) if "commodity_id" in df.columns else []
    comm_sel = c4.multiselect("Commodity", comms, key="hh_comm")
    mkts = sorted(df["market_id"].dropna().astype(str).unique()) if "market_id" in df.columns else []
    mkt_sel = c5.multiselect("Market", mkts, key="hh_mkt")
    thr = c6.slider("Decision threshold", 0.0, 1.0, 0.5, 0.01, key="hh_thr")

    sub = df.copy()
    if msel:
        sub = sub[sub["month"].dt.strftime("%Y-%m").isin(msel)]
    if dsel:
        sub = sub[sub["district"].isin(dsel)]
    if csel and "category" in sub.columns:
        sub = sub[sub["category"].astype(str).isin(csel)]
    if comm_sel and "commodity_id" in sub.columns:
        sub = sub[sub["commodity_id"].astype(str).isin(comm_sel)]
    if mkt_sel and "market_id" in sub.columns:
        sub = sub[sub["market_id"].astype(str).isin(mkt_sel)]
    sub = sub.copy()
    sub["flagged"] = sub[model_col] >= thr
    sub["outcome"] = np.where(sub[ycol] == 1, "Stress observed", "No stress")

    st.caption(f"{F.intc(len(sub))} of {F.intc(len(df))} scored rows · "
               f"holdout window {F.date_range(df['month'])} · target {ycol.upper()} · "
               f"source artefacts/preds_{task}.parquet")

    if sub.empty:
        st.info("No rows match the current filters.")
        return

    prev = float(df[ycol].mean())
    L.kpi_row([
        {"icon": "🎯", "color": "#F5F3FF", "label": "Mean score",
         "value": F.num(sub[model_col].mean(), 3), "caption": "selected model"},
        {"icon": "🚩", "color": "#FEF2F2", "label": "Flagged at threshold",
         "value": F.pct(sub["flagged"].mean()), "caption": f"threshold {F.num(thr,2)}"},
        {"icon": "📊", "color": "#EFF6FF", "label": "Observed stress",
         "value": F.pct(sub[ycol].mean()), "caption": f"holdout prevalence {F.pct(prev)}"},
        {"icon": "🧾", "color": "#F0FDF4", "label": "Rows",
         "value": F.intc(len(sub)), "caption": "after filters"},
    ])
    st.write("")

    tabs = st.tabs(["Ranked table", "Distribution", "Observed vs predicted", "Map", "Data"])

    with tabs[0]:
        L.section("Ranked predictions", "Highest model scores first.")
        top = sub.sort_values(model_col, ascending=False).head(50).copy()
        show = [c for c in ["month", "commodity_id", "district", "category",
                            model_col, "flagged", "outcome"] if c in top.columns]
        view = top[show]
        if model_col in view:
            view = view.assign(**{model_col: view[model_col].round(3)})
        st.dataframe(view, use_container_width=True, hide_index=True)

    with tabs[1]:
        L.section("Predicted probability distribution", "Score histogram with threshold line.")
        fig = C.histogram(sub[model_col].dropna(), bins=30, x_title="Predicted probability",
                          height=320)
        try:
            fig.add_vline(x=thr, line_dash="dash", line_color="#C4921C",
                          annotation_text=f"threshold {thr:.2f}")
        except Exception:
            pass
        C.show(fig)
        st.caption(f"Mean {F.num(sub[model_col].mean(),3)} · "
                   f"p90 {F.num(sub[model_col].quantile(0.9),3)} · n {F.intc(len(sub))}.")

    with tabs[2]:
        L.section("Observed vs predicted", "Confusion and calibration-style view.")
        tp = int(((sub[model_col] >= thr) & (sub[ycol] == 1)).sum())
        fp = int(((sub[model_col] >= thr) & (sub[ycol] == 0)).sum())
        fn = int(((sub[model_col] < thr) & (sub[ycol] == 1)).sum())
        tn = int(((sub[model_col] < thr) & (sub[ycol] == 0)).sum())
        C.show(C.confusion(np.array([[tn, fp], [fn, tp]], dtype=float), ["Neg", "Pos"],
                           title=f"{MODEL_LABELS.get(model_col, model_col)} at thr {thr:.2f}"))
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("TP", F.intc(tp))
        c2.metric("FP", F.intc(fp))
        c3.metric("FN", F.intc(fn))
        c4.metric("TN", F.intc(tn))
        st.caption("Counts are recomputed from the stored holdout scores at the chosen "
                   "threshold; they are not official classifications.")

    with tabs[3]:
        L.section("Historical map", "Mean score by district over the holdout window.")
        geo = D.load_geo()
        if geo is None or "district" not in sub.columns:
            L.unavailable("the map", "raw/geo/zwe_adm2_geoboundaries.geojson")
        else:
            agg = sub.groupby("district")[model_col].mean().reset_index()
            geonames = {f["properties"]["shapeName"] for f in geo["features"]}
            agg = agg[agg["district"].isin(geonames)]
            if agg.empty:
                L.unavailable("the map (no matching district names)")
            else:
                C.show(C.choropleth(agg, geo, "district", model_col, height=380,
                                    colorbar_title="Mean score", vmin=0.0, vmax=1.0,
                                    colorscale="YlOrRd"))
            st.caption("Districts without scored rows are not coloured. Predicted values are "
                       "model outputs, not household food insecurity.")

    with tabs[4]:
        L.section("Filtered rows", "Download the current filtered predictions.")
        st.dataframe(sub.head(1000), use_container_width=True, hide_index=True)
        st.download_button("Download filtered predictions (CSV)",
                           sub.to_csv(index=False).encode("utf-8"),
                           file_name=f"{task}_filtered_holdout.csv")
        st.caption("Historical holdout output; not a prospective forecast.")

    st.caption(f"Note: {L.DISCLAIMER}")
