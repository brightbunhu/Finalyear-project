"""About & Help — editorial project background, technical methodology, and limitations."""
from __future__ import annotations

import streamlit as st
from components import layout as L

LIMITATIONS = [
    ("No prospective operational validation", "error",
     "All reported evaluation metrics are strictly retrospective (expanding-window time-series CV plus a single 12-month forward holdout). No prospective live operational forecasting trial has been conducted.",
     "artifacts/metrics_all_tasks.csv (splits: cv_pooled, holdout)",
     "Treat every prediction score as a retrospective econometric estimate, not an official early-warning alert."),
    ("Local data snapshot rather than live API feed", "warning",
     "The system operates on an offline harmonized dataset snapshot. It does not poll live web APIs in real time; the latest available date reflects when the data integration pipeline was executed.",
     "data_processed/panel_usdprice.parquet (month max)",
     "Check data coverage and last observation date before interpreting temporal recency."),
    ("Market stress is distinct from household food insecurity", "warning",
     "The prediction targets evaluate market price stress (accelerating month-over-month return surges or local prices exceeding peer medians). While market prices strongly constrain food access, price stress does not measure household consumption deficits, coping mechanisms, or acute malnutrition.",
     "reports/phase2_target_definition.md",
     "Do not conflate price spikes directly with IPC Phase 3+ food-insecurity classifications."),
    ("Currency regime heterogeneity", "warning",
     "The Zimbabwean economy experienced multiple currency transitions (USD multicurrency, RTGS/ZWL, ZiG). USD and nominal series represent completely different monetary regimes and are modeled in separate tasks (T1/T2 vs T3/T4); they are never pooled together.",
     "data_processed/panel_usdprice.parquet & panel_nominal_within_currency.parquet",
     "Never compare nominal local-currency price movements with USD converted prices without adjusting for the currency regime."),
    ("Sampling sparsity in remote market centers", "info",
     "Certain remote rural markets exhibit intermittent monthly price reporting. Consequently, rolling multi-month features require careful backward imputation or are marked as missing.",
     "reports/phase1_data_quality_report.md",
     "Interpret predictions for sparsely sampled markets alongside the sample size indicator."),
    ("Indirect climate relationship", "info",
     "CHIRPS rainfall anomalies serve as secondary background indicators. Empirical lead-lag correlation between monthly rainfall deficits and food prices is non-linear and moderated by regional grain imports.",
     "reports/phase6_lead_lag.csv, reports/phase6b_diagnostics.md",
     "Do not interpret rainfall deficits as the sole mechanical driver of price acceleration."),
    ("Model uncertainty and confidence intervals", "info",
     "Predictions carry inherent statistical variance. Bootstrapped 95% confidence intervals indicate higher predictive precision for spatial peer stress (Y2) than for high-frequency return surges (Y1).",
     "reports/phase6b_bootstrap_ci.csv",
     "Always consult the confidence bounds and baseline historical prevalence."),
]

GLOSSARY = [
    ("Spatial Price Index (SPI)", "The ratio of a local market's price to the contemporaneous national median price for that commodity ($SPI = P_{i,t} / \\tilde{P}_t$). Values $\\ge 1.20$ indicate that the market is at least 20% more expensive than national peers."),
    ("Return Surge (Y1 Target)", "A binary indicator for whether the month-over-month price return exceeds the historical district mean by at least 1.0 standard deviation ($Z_{r} \\ge +1.0\\sigma$)."),
    ("Peer-Relative Stress (Y2 Target)", "A binary indicator triggered when a market's Spatial Price Index meets or exceeds 1.20 ($SPI \\ge 1.20$), signifying acute localized price divergence."),
    ("CHIRPS Precipitation Anomaly ($Z_{rain}$)", "Standardized monthly precipitation deviation relative to the 1981–2015 historical climatological baseline. Negative values signify meteorological drought."),
    ("Expanding-Window Cross-Validation", "A temporal validation strategy where training folds strictly precede test folds in time, preventing future-data leakage in financial and economic forecasting."),
    ("Brier Score", "A strictly proper scoring rule measuring the accuracy of probabilistic forecasts; lower values indicate better calibration and sharper probability estimates."),
]


def render() -> None:
    L.page_header(
        "About & Help",
        "Project methodology, food-security context, data architecture, technical glossary, and research limitations.",
        provenance="Compiled from project dissertation chapters, methodology reports, and empirical artefacts."
    )

    tab_about, tab_limits = st.tabs(["About the Project", "Limitations & Interpretation"])

    with tab_about:
        L.section("Project Scope & Mission")
        st.markdown(
            """
            This research dashboard provides an **empirical machine-learning early-warning framework** for monitoring and predicting
            staple food-price stress across administrative districts in Zimbabwe. By harmonizing granular market transaction records with
            gridded meteorological anomalies and spatial geographic boundaries, the platform evaluates whether modern gradient boosting
            and regularized econometrics can detect localized price stress **one month in advance**.
            """
        )

        a1, a2, a3 = st.columns(3, gap="medium")
        with a1:
            L.card(
                '<div style="font-size:12px;font-weight:700;color:var(--blue);text-transform:uppercase;">1. Data Harmonization</div>'
                '<div style="font-size:15px;font-weight:700;color:var(--navy);margin:4px 0 6px;">Multi-Source Integration</div>'
                '<p style="font-size:13px;color:var(--text-secondary);line-height:1.5;margin:0;">'
                'Integrates WFP market prices, CHIRPS precipitation netCDF grids, geoBoundaries polygons, and UN OCHA HDX population estimates into a harmonized monthly panel.</p>'
            )
        with a2:
            L.card(
                '<div style="font-size:12px;font-weight:700;color:var(--teal);text-transform:uppercase;">2. Target Engineering</div>'
                '<div style="font-size:15px;font-weight:700;color:var(--navy);margin:4px 0 6px;">Econometric Formulations</div>'
                '<p style="font-size:13px;color:var(--text-secondary);line-height:1.5;margin:0;">'
                'Distinguishes between temporal acceleration (Y1: standardized return surge $\\ge 1.0\\sigma$) and spatial market divergence (Y2: Spatial Price Index $\\ge 1.20x$).</p>'
            )
        with a3:
            L.card(
                '<div style="font-size:12px;font-weight:700;color:var(--purple);text-transform:uppercase;">3. Strict Validation</div>'
                '<div style="font-size:15px;font-weight:700;color:var(--navy);margin:4px 0 6px;">No Leakage Verification</div>'
                '<p style="font-size:13px;color:var(--text-secondary);line-height:1.5;margin:0;">'
                'Models are evaluated through expanding-window time-series splits and locked 12-month forward temporal holdout tests, strictly preventing look-ahead bias.</p>'
            )

        st.write("")
        L.section("The Zimbabwe Food-Price Context")
        st.markdown(
            """
            In Zimbabwe, household food security is intimately bound to staple cereal affordability (particularly white maize grain and roller meal).
            Rural markets in arid southern and western districts (e.g., Mwenezi, Chiredzi, Beitbridge) frequently experience pronounced price premiums
            due to long transport distances from surplus grain basins (Mashonaland Central and West). 

            Coupled with recurrent El Niño-induced rainfall shocks and macroeconomic currency transitions, early identification of market stress
            is crucial for grain routing, targeted cash transfers, and proactive humanitarian intervention.
            """
        )

        st.write("")
        L.section("Technical Architecture")
        st.markdown(
            """
            - **Data Processing**: Vectorized Pandas and PyArrow pipelines computing lag price returns ($t-1$, $t-2$), 3-month rolling return momentum, spatial median benchmarks, and climatological precipitation z-scores.
            - **Machine Learning Estimators**: Scikit-Learn `HistGradientBoostingClassifier`, `LogisticRegression` with ElasticNet penalty, and `XGBClassifier`, trained with stratified class weights.
            - **Hyperparameter Optimization**: Automated 50-trial Optuna Bayesian search optimizing holdout PR-AUC and ROC-AUC.
            - **Serving**: Pure Python Streamlit application utilizing `@st.cache_data` and `@st.cache_resource` for zero-redundancy interactive responsiveness.
            """
        )

    with tab_limits:
        L.section("Scientific Limitations Register", "Explicit methodological caveats linked directly to project evaluation evidence.")

        for title, kind, text, evidence, advice in LIMITATIONS:
            badge_kind = "very-high" if kind == "error" else ("high" if kind == "warning" else "info")
            st.markdown(
                f'<div class="card" style="margin-bottom:12px; border-left: 4px solid var(--{"risk-very-high" if kind=="error" else "amber" if kind=="warning" else "blue"});">'
                f'<div style="display:flex; justify-content:space-between; align-items:center;">'
                f'<b style="font-size:14px; color:var(--navy);">{L.esc(title)}</b>'
                f'<span class="badge {badge_kind}">{kind.upper()}</span>'
                f'</div>'
                f'<p style="font-size:13px; color:var(--text-primary); margin:6px 0 8px; line-height:1.5;">{L.esc(text)}</p>'
                f'<div style="font-size:11.5px; color:var(--text-secondary);"><b>Evidence source:</b> <code>{L.esc(evidence)}</code></div>'
                f'<div style="font-size:11.5px; color:var(--navy); margin-top:3px;"><b>Operational recommendation:</b> {L.esc(advice)}</div>'
                f'</div>', unsafe_allow_html=True
            )

        st.write("")
        L.section("Technical Glossary")
        for term, definition in GLOSSARY:
            st.markdown(f"**{term}**: {definition}")

        st.write("")
        L.section("Troubleshooting & Verification")
        st.markdown(
            """
            - **Missing Data or Cards Showing 'Unavailable'**: The system only displays verified facts from stored pipeline files in `artifacts/`, `models/`, and `data_processed/`. If a file was not generated, the application renders a clean notice rather than substituting fabricated data.
            - **Slow Refresh**: All large datasets are cached in memory using `st.cache_data`. If you modify pipeline artefacts, restart the Streamlit server or press `C` in the browser to clear cache.
            - **Reproducibility**: All model seeds (fixed to `42`), training configurations, and fold dates are recorded in `artifacts/run_metadata.json`.
            """
        )
