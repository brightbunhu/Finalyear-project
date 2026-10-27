"""Model Performance — transparent evaluation evidence and validation boundaries."""
from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from components import layout as L
from components import charts as C
from components import filters as CF
from utils import loaders as D
from utils import formatting as F

MODEL_LABELS = {
    "majority": "Majority baseline",
    "persistence": "Persistence baseline",
    "logistic_elasticnet": "Logistic (elastic net)",
    "hist_gradient_boosting": "Hist gradient boosting",
    "xgboost": "XGBoost",
}


def _confusion_fig(row: pd.Series):
    cm = np.array([[row["tn"], row["fp"]], [row["fn"], row["tp"]]], dtype=float)
    return C.confusion(cm, ["Neg", "Pos"], title=f"{MODEL_LABELS.get(row['model'], row['model'])} "
                                                f"· {row['split']}")


def render() -> None:
    L.page_header("Model Performance",
                  "Compare models, evaluate predictive quality, and inspect validation results.",
                  provenance="artifacts/metrics_all_tasks.csv, artifacts/folds_*.json, models/*.meta.json, figures/")

    metrics = D.load_metrics()
    if metrics.empty:
        L.unavailable("the metrics file", "artifacts/metrics_all_tasks.csv")
        return

    tasks = sorted(metrics["task"].unique())
    task = st.selectbox("Task (base · target)", tasks, key="mp_task")
    sub = metrics[metrics["task"] == task].copy()
    base = sub["base"].iloc[0]
    target = sub["target"].iloc[0]

    note = ("Performance varies by target. Y2 is partly persistence-driven, while Y1 is "
            "more difficult. Do not compare scores across different targets as if they "
            "measured the same task.")
    st.info(note)
    st.caption("Cross-validation (cv_pooled) and forward holdout are shown separately. "
               "Metrics are never pooled across tasks or splits.")

    # model summary from metadata where available
    meta_name = None
    for name, (t, b, y) in D.MODEL_NAMES.items():
        if t == task:
            meta_name = name
    if meta_name:
        _, meta = D.load_model(meta_name)
    else:
        meta = None

    ho = sub[sub["split"] == "holdout"].sort_values("roc_auc", ascending=False)
    best = ho.iloc[0] if not ho.empty else sub.iloc[0]

    L.kpi_row([
        {"icon": "🎯", "color": "#F5F3FF", "label": "Best holdout ROC-AUC",
         "value": F.num(best["roc_auc"], 3),
         "caption": f"{MODEL_LABELS.get(best['model'], best['model'])}"},
        {"icon": "📐", "color": "#EFF6FF", "label": "Best holdout PR-AUC",
         "value": F.num(ho["pr_auc"].max(), 3) if not ho.empty else "—",
         "caption": "Precision–recall area"},
        {"icon": "⚖️", "color": "#F0FDF4", "label": "Balanced accuracy",
         "value": F.num(best["balanced_accuracy"], 3),
         "caption": "At the reported threshold"},
        {"icon": "📉", "color": "#FEF9C3", "label": "Brier score",
         "value": F.num(best["brier"], 3), "caption": "Lower is better"},
    ])
    st.write("")

    if meta:
        def card(inner):
            L.card(inner)
        with st.expander("Model & validation boundaries", expanded=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                card(f'<div class="metric-lbl">Estimator</div>'
                     f'<div class="metric-val" style="font-size:15px">{L.esc(meta.get("model"))}</div>'
                     f'<div class="metric-cap">seed {meta.get("seed")} · {L.esc(meta.get("config_version"))}</div>')
            with c2:
                card(f'<div class="metric-lbl">Training boundary</div>'
                     f'<div class="metric-val" style="font-size:15px">{F.month_label(meta.get("trained_through"))}</div>'
                     f'<div class="metric-cap">holdout from {F.month_label(meta.get("holdout_from"))}</div>')
            with c3:
                n_feat = len(meta.get("features_numeric", [])) + len(meta.get("features_categorical", []))
                card(f'<div class="metric-lbl">Features / train rows</div>'
                     f'<div class="metric-val" style="font-size:15px">{n_feat} / {F.intc(meta.get("n_train"))}</div>'
                     f'<div class="metric-cap">prevalence {F.pct(meta.get("prevalence_train"))}</div>')
            st.caption(f"Source artefact: models/{meta_name}.joblib · {meta_name}.meta.json")

    tabs = st.tabs(["Comparison", "Confusion matrix", "Curves", "Calibration", "Importance",
                    "Threshold & robustness", "Full table"])

    with tabs[0]:
        L.section("Metric comparison by model and split",
                  "ROC-AUC / PR-AUC / F1 by model, CV and holdout kept separate.")
        piv = sub.pivot_table(index="model", columns="split",
                              values=["roc_auc", "pr_auc", "f1"])
        st.dataframe(piv.round(3), use_container_width=True)
        gsrc = CF.chart_filters(sub, "mp_compare", include=["model", "split"])
        g = gsrc.melt(["model", "split"], value_vars=["roc_auc", "pr_auc"],
                      var_name="metric", value_name="value")
        if g.empty:
            st.info("No rows match the chart filters.")
        for split in sorted(gsrc["split"].unique()) if not gsrc.empty else []:
            ss = g[g["split"] == split]
            if not ss.empty:
                st.markdown(f"**{split}**")
                C.show(C.multi_line(ss, "model", "value", "metric", height=280,
                                    y_title="Score"))
        st.caption("Baselines (majority, persistence) are included for reference. "
                   "Y1 and Y2 belong to different tasks.")

    with tabs[1]:
        L.section("Confusion matrices", "At the reported threshold; cells are counts.")
        split_sel = st.radio("Split", sorted(sub["split"].unique()), horizontal=True, key="mp_cm_split")
        rows = CF.chart_filters(sub[sub["split"] == split_sel], "mp_cm", include=["model"])
        if rows.empty:
            st.info("No rows match the chart filters.")
            rows = rows.iloc[0:0]
        cols = st.columns(min(3, len(rows)) or 1)
        for i, (_, r) in enumerate(rows.iterrows()):
            with cols[i % len(cols)]:
                C.show(_confusion_fig(r))
                st.caption(f"n={F.intc(r['n'])} · threshold {F.num(r['threshold'], 2)} · "
                           f"pos={F.intc(r['pos'])}")

    with tabs[2]:
        L.section("ROC and precision–recall curves", "Pre-generated from the evaluation pipeline.")
        keymap = {"T1_usd_y1": ("roc_T1", "pr_T1"), "T2_usd_y2": ("roc_T2", "pr_T2"),
                  "T3_nominal_y1": ("roc_T3", "pr_T3"), "T4_nominal_y2": ("roc_T4", "pr_T4")}
        rk, pk = keymap.get(task, (None, None))
        c1, c2 = st.columns(2)
        rp = D.fig_path(D.FIGURES[rk]) if rk else None
        pp = D.fig_path(D.FIGURES[pk]) if pk else None
        with c1:
            if rp:
                st.image(str(rp), caption="ROC curve")
            else:
                L.unavailable("ROC figure", f"figures/{D.FIGURES.get(rk, '')}")
        with c2:
            if pp:
                st.image(str(pp), caption="Precision–recall curve")
            else:
                L.unavailable("PR figure")

    with tabs[3]:
        L.section("Calibration", "Predicted probability vs observed frequency.")
        ck = {"T1_usd_y1": "calibration_T1", "T2_usd_y2": "calibration_T2",
              "T3_nominal_y1": "calibration_T1", "T4_nominal_y2": "calibration_T2"}.get(task)
        cp = D.fig_path(D.FIGURES[ck]) if ck else None
        if cp:
            st.image(str(cp), caption="Calibration plot")
        else:
            L.unavailable("calibration figure")
        st.caption("Calibration may vary by threshold; see Brier score in the full table.")

    with tabs[4]:
        L.section("Feature importance", "Permutation importance where available.")
        imp = D.load_perm_importance(task)
        if imp.empty:
            L.unavailable("permutation importance",
                          f"artifacts/perm_importance_{task}.csv is empty or missing",
                          "Permutation-importance figures may still be available below.")
        else:
            st.dataframe(imp, use_container_width=True, hide_index=True)
        ik = {"T1_usd_y1": "importance_T1", "T2_usd_y2": "importance_T2"}.get(task)
        ip = D.fig_path(D.FIGURES[ik]) if ik else None
        if ip:
            st.image(str(ip), caption="Feature-importance figure")
        st.caption("Importance is unstable across folds (see robustness diagnostics).")

    with tabs[5]:
        L.section("Threshold sensitivity & robustness",
                  "Threshold sweep and robustness diagnostics from reports/.")
        tp = D.fig_path(D.FIGURES["threshold_prevalence"])
        if tp:
            st.image(str(tp), caption="Threshold sensitivity")
        rob = D.load_report_csv("phase6b_threshold_model_sensitivity.csv")
        if not rob.empty:
            st.dataframe(rob, use_container_width=True, hide_index=True)
        with st.expander("Bootstrap confidence intervals"):
            ci = D.load_report_csv("phase6b_bootstrap_ci.csv")
            if not ci.empty:
                st.dataframe(ci, use_container_width=True, hide_index=True)
                st.caption("Market-clustered bootstrap. The Y1 interval can include chance.")
            else:
                L.unavailable("bootstrap CI file", "reports/phase6b_bootstrap_ci.csv")

    with tabs[6]:
        L.section("Full metrics table", "All rows for the selected task.")
        st.dataframe(sub.round(4), use_container_width=True, hide_index=True)
        st.download_button("Download task metrics (CSV)",
                           sub.to_csv(index=False).encode("utf-8"),
                           file_name=f"metrics_{task}.csv")

    st.warning("Do not claim the model is operationally validated without prospective evidence. "
               "All results here are retrospective.")
    st.caption(f"Note: {L.DISCLAIMER}")
