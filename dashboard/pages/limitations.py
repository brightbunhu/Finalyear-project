"""Limitations & Interpretation — plain-language scope and caveats, grounded in artefacts."""
from __future__ import annotations

import streamlit as st

from components import layout as L

LIMITATIONS = [
    ("No prospective validation", "error",
     "All reported metrics are retrospective: expanding-window cross-validation plus a "
     "single forward holdout. No prospective or operational trial has been run.",
     "artifacts/metrics_all_tasks.csv (splits: cv_pooled, holdout)",
     "Model Performance, Historical Holdout Predictions, Prediction Studio, Home",
     "Treat every score as a retrospective estimate, not a validated warning."),
    ("Latest snapshot is local, not live", "warning",
     "The dashboard reads a local snapshot built from stored source files. It does not "
     "pull live external data, so the 'latest month' reflects when the pipeline last ran.",
     "data_processed/panel_usdprice.parquet (month max)",
     "Home, Coverage & Quality, Price Trends, Data & Integration",
     "Check the latest month before interpreting recency."),
    ("Sparse market–commodity series", "warning",
     "Median series length is short, so only a minority of cells have a usable next-month "
     "label. Short series weaken both features (lag/rolling returns) and evaluation.",
     "reports/phase1_data_quality_report.md; panel labelable_y1/labelable_y2",
     "Coverage & Quality, Statistical Analysis, Model Performance",
     "Report the labelable share alongside any headline metric."),
    ("Currency-regime differences", "warning",
     "USD and nominal (within-currency) bases represent different regimes and are never "
     "pooled. Nominal prices across currencies are not directly comparable.",
     "data_processed/panel_usdprice.parquet; panel_nominal_within_currency.parquet",
     "Price Trends, Model Performance, Statistical Analysis, Geographic Explorer",
     "Never compare nominal prices across currencies without a documented conversion."),
    ("Missing or incomplete source files", "info",
     "Some expected artefacts (for example empty permutation-importance files) may be "
     "absent. The UI shows an explicit unavailable state instead of substituting values.",
     "artifacts/perm_importance_*.csv (empty); figures/ (present)",
     "Data & Integration, Model Performance",
     "Missingness is reported, never silently filled."),
    ("Missing geographic coordinates", "warning",
     "A small number of markets lack coordinates, so they cannot be placed on the map; "
     "district boundaries are matched by name and may leave some areas uncoloured.",
     "data_processed/market_admin_crosswalk.csv; raw/geo/zwe_adm2_geoboundaries.geojson",
     "Geographic Explorer, Home, Rainfall & Climate",
     "Absence from a map is a coverage artefact, not evidence of low risk."),
    ("Weak rainfall association", "info",
     "Rainfall is treated as an indirect predictor. The measured rainfall–return lead–lag "
     "association is weak and unstable across folds, so rainfall should not be read as a "
     "driver of price stress.",
     "reports/phase6_lead_lag.csv; reports/phase6b_diagnostics.md",
     "Rainfall & Climate, Statistical Analysis, Model Performance",
     "Do not infer that rainfall causes price stress."),
    ("Y2 is partly persistence-driven", "info",
     "The peer-relative target (Y2) is partly predictable from the current state, so its "
     "higher scores partly reflect persistence rather than independent forecasting skill.",
     "models/y2_peer_histgbm_usd.meta.json; reports/phase6b_diagnostics.md",
     "Model Performance, Historical Holdout Predictions, Statistical Analysis",
     "Y1 and Y2 are different tasks; their scores are not comparable."),
    ("Model uncertainty", "info",
     "Probabilities carry sampling and model uncertainty. Bootstrap intervals for Y1 can "
     "reach chance, and calibration varies by threshold.",
     "reports/phase6b_bootstrap_ci.csv; figures/fig4.4.4.*",
     "Model Performance, Prediction Studio",
     "A probability is an estimate with error, not a certainty."),
    ("Market stress ≠ household food insecurity", "info",
     "Targets measure market price stress (standardised returns, or a market's price "
     "relative to peers). This is not the same as household food insecurity.",
     "reports/phase2_target_definition.md",
     "Home, Historical Holdout Predictions, Limitations",
     "Do not present market-price stress as household food-security status."),
    ("Outputs are not official warnings", "error",
     "Model outputs are research evidence only. They are not official early-warning "
     "products or food-security classifications.",
     "Repository disclaimer (all pages)",
     "All pages",
     "Cite as research evidence, never as an operational alert."),
]


def _affected_links(text: str) -> str:
    parts = [p.strip() for p in text.split(",")]
    return " · ".join(L.badge(p, "na") for p in parts)


def render() -> None:
    L.page_header("Limitations & Interpretation",
                  "What the data and models can and cannot support, in plain language.",
                  provenance="Derived from repository reports, model metadata and evaluation artefacts.")

    n_evidenced = sum(1 for x in LIMITATIONS if x[1] in ("warning", "error"))
    L.kpi_row([
        {"icon": "⚠️", "color": "#FEF2F2", "label": "Documented limitations",
         "value": str(len(LIMITATIONS)), "caption": "Evidence-linked caveats below"},
        {"icon": "🔬", "color": "#F5F3FF", "label": "Validation type",
         "value": "Retrospective", "caption": "CV + single forward holdout"},
    ])
    st.write("")

    L.section("Limitation register",
              "Each item states the caveat, its evidence, the pages it affects and how to interpret it.")

    severity = {"error": ("error", "Serious"), "warning": ("warning", "Caveat"),
                "info": ("info", "General caution")}
    for i, (title, kind, explanation, evidence, pages, guidance) in enumerate(LIMITATIONS, 1):
        cls, label = severity.get(kind, ("info", "Note"))
        with st.expander(f"{i}. {title}", expanded=(i <= 2)):
            st.markdown(f"{L.badge(label, cls)}", unsafe_allow_html=True)
            st.markdown(explanation)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Evidence / source**")
                st.caption(evidence)
            with c2:
                st.markdown("**Interpretation guidance**")
                st.caption(guidance)
            st.markdown("**Affected pages**")
            st.markdown(_affected_links(pages), unsafe_allow_html=True)

    st.write("")
    L.section("Scope statement")
    st.info("This dashboard supports exploratory and descriptive analysis of market price "
            "stress for a research dissertation. It is not an operational early-warning "
            "system, and it does not provide household-level food-security assessments.")
    st.caption(f"Note: {L.DISCLAIMER}")
