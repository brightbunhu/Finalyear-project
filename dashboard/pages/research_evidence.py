"""Research Evidence — connect the dashboard to objectives and implementation artefacts."""
from __future__ import annotations

import streamlit as st

from components import layout as L
from utils import loaders as D

# Grouping is provisional (the repository does not store verbatim dissertation
# objectives in a machine-readable artefact), and is labelled as such in the UI.
OBJECTIVES = [
    ("Data integration", "Integrate food prices, markets, rainfall and population into a "
     "single model-ready panel.",
     ["data_processed/panel_usdprice.parquet", "data_processed/market_admin_crosswalk.csv",
      "data_processed/rainfall_district_month_anom.parquet"],
     "Data & Integration", "Data & Integration"),
    ("Target construction", "Define and document two distinct stress targets (Y1 standardised-"
     "return stress, Y2 peer-relative stress) with no label leakage.",
     ["reports/phase2_target_definition.md", "tests/run_checks.py"],
     "Coverage & Quality, Statistical Analysis", "Statistical Analysis"),
    ("Predictive modelling", "Train and evaluate multiple learners against baselines under "
     "expanding-window CV and a forward holdout.",
     ["artifacts/metrics_all_tasks.csv", "models/y2_peer_histgbm_usd.meta.json",
      "artifacts/optuna_summary.csv"],
     "Model Performance, Prediction Studio", "Model Performance"),
    ("Geographic analysis", "Explore spatial variation in prices, stress and model scores "
     "using real boundaries.",
     ["raw/geo/zwe_adm2_geoboundaries.geojson", "data_processed/market_admin_crosswalk.csv"],
     "Geographic Explorer, Home", "Geographic Explorer"),
    ("Reproducibility & limitations", "Provide traceable artefacts, robustness diagnostics "
     "and an explicit limitations register.",
     ["reports/phase6b_diagnostics.md", "reports/phase10_qa_and_limitations.md",
      "tests/run_checks.py"],
     "Research Evidence, Limitations & Interpretation", "Limitations & Interpretation"),
]

EVIDENCE_STATUS = {
    "data_processed/panel_usdprice.parquet": ("Evidenced", "ok"),
    "data_processed/panel_nominal_within_currency.parquet": ("Evidenced", "ok"),
    "data_processed/market_admin_crosswalk.csv": ("Evidenced", "ok"),
    "data_processed/rainfall_district_month_anom.parquet": ("Evidenced", "ok"),
    "reports/phase2_target_definition.md": ("Evidenced", "ok"),
    "tests/run_checks.py": ("Evidenced", "ok"),
    "artifacts/metrics_all_tasks.csv": ("Evidenced", "ok"),
    "models/y2_peer_histgbm_usd.meta.json": ("Evidenced", "ok"),
    "artifacts/optuna_summary.csv": ("Evidenced", "ok"),
    "raw/geo/zwe_adm2_geoboundaries.geojson": ("Evidenced", "ok"),
    "reports/phase6b_diagnostics.md": ("Evidenced", "ok"),
    "reports/phase10_qa_and_limitations.md": ("Evidenced", "ok"),
}


def _status_for(path_str: str) -> tuple[str, str]:
    p = D.ROOT / path_str
    if not p.exists():
        return "Unavailable", "na"
    return EVIDENCE_STATUS.get(path_str, ("Evidenced", "ok"))


def render() -> None:
    L.page_header("Research Evidence",
                  "Map each objective to the dashboard and to concrete implementation artefacts.",
                  provenance="Statuses reflect whether the referenced artefact exists in the repository.")

    st.warning("Objective groupings below are provisional (the repository does not contain a "
               "machine-readable list of verbatim dissertation objectives). They should not be "
               "quoted as exact dissertation wording.")

    # objective cards
    cols = st.columns(2, gap="small")
    for i, (name, desc, paths, page_ref, _nav) in enumerate(OBJECTIVES):
        present = sum(1 for p in paths if (D.ROOT / p).exists())
        status = "Evidenced" if present == len(paths) else (
            "Partially evidenced" if present else "Unavailable")
        cls = "ok" if present == len(paths) else ("med" if present else "na")
        with cols[i % 2]:
            L.card(
                f'{L.badge(status, cls)}'
                f'<div class="metric-lbl" style="margin-top:8px">{L.esc(name)}</div>'
                f'<div class="stage-desc" style="margin-top:4px">{L.esc(desc)}</div>'
                f'<div class="metric-cap" style="margin-top:8px">Implemented in: '
                f'<b>{L.esc(page_ref)}</b></div>'
                f'<div class="metric-cap">Artefacts present: {present}/{len(paths)}</div>')
            st.write("")

    st.write("")
    L.section("Evidence matrix",
              "Searchable list of claims, evidence sources and statuses.")
    path_filter = st.multiselect("Filter by objective", [o[0] for o in OBJECTIVES])

    rows = []
    for name, desc, paths, page_ref, _nav in OBJECTIVES:
        if path_filter and name not in path_filter:
            continue
        for p in paths:
            status, _ = _status_for(p)
            rows.append({
                "Objective": name,
                "Claim": desc,
                "Artefact path": p,
                "Dashboard location": page_ref,
                "Status": status,
            })
    st.dataframe(rows, use_container_width=True, hide_index=True)

    tot = len(rows)
    evid = sum(1 for r in rows if r["Status"] == "Evidenced")
    L.kpi_row([
        {"icon": "✅", "color": "#ECFDF5", "label": "Evidence links evidenced",
         "value": f"{evid}/{tot}", "caption": "Referenced artefact exists in repo"},
        {"icon": "📚", "color": "#F5F3FF", "label": "Robustness reports",
         "value": str(sum(1 for p in D.REP.glob('phase6b_*.csv'))),
         "caption": "reports/phase6b_*.csv"},
        {"icon": "🧪", "color": "#EFF6FF", "label": "QA checks",
         "value": "tests/run_checks.py", "caption": "Dependency-free assertion suite"},
    ])

    st.caption("A status of 'Evidenced' means the referenced artefact exists and supports the "
               "claim; it does not imply the objective is fully met for the dissertation.")
