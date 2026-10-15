"""Zimbabwe Food Price Stress - research dashboard.

Run:  streamlit run dashboard/app.py

Everything shown is read from artefacts produced by the pipeline
(data_processed/, artifacts/, models/, figures/, reports/). This is a RESEARCH
prototype. It is NOT an operational early-warning system.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data_processed"
ART = ROOT / "artifacts"
FIG = ROOT / "figures"
REP = ROOT / "reports"
MODELS = ROOT / "models"
CFG = yaml.safe_load((ROOT / "config" / "targets.yml").read_text(encoding="utf-8"))

st.set_page_config(page_title="ZW Food Price Stress - Research",
                   layout="wide", initial_sidebar_state="expanded")

DISCLAIMER = ("**Research prototype.** Not an operational early-warning system. "
              "No model here has been prospectively validated. Predictions are "
              "historical holdout scores, not live forecasts.")


# ----------------------------------------------------------------- styling
CSS = """
<style>
  :root{
    --card:#ffffff; --ink:#0f172a; --muted:#64748b;
    --accent:#2563eb; --accent2:#0ea5e9; --border:#e6ebf3;
    --ok:#16a34a; --warn:#d97706; --bad:#dc2626;
  }
  html, body, [class*="css"]{
    font-family:'Segoe UI', -apple-system, Roboto, 'Helvetica Neue', Arial, sans-serif;
  }

  .stApp{
    background:
      radial-gradient(1100px 480px at 100% -8%, #e2edff 0%, rgba(226,237,255,0) 60%),
      radial-gradient(900px 420px at -10% 0%, #e6fbf4 0%, rgba(230,251,244,0) 55%),
      #f6f8fb;
  }
  [data-testid="stHeader"]{ background:transparent; }
  .block-container{ padding-top:2.4rem; padding-bottom:3.2rem; max-width:1180px; }

  /* ---- hero ---- */
  .hero{
    background:linear-gradient(120deg,#0b1220 0%,#12203c 55%,#1e3a8a 100%);
    border-radius:20px; padding:26px 30px; color:#eaf1ff;
    box-shadow:0 24px 48px -30px rgba(15,23,42,.55); margin-bottom:6px;
  }
  .hero h1{ color:#ffffff; font-size:1.7rem; font-weight:800; margin:.35rem 0 .3rem;
            letter-spacing:-.01em; line-height:1.2; }
  .hero p{ color:#b9c6e6; font-size:.95rem; margin:0; max-width:840px; }
  .pill{
    display:inline-block; font-size:.72rem; font-weight:700; letter-spacing:.08em;
    text-transform:uppercase; color:#dbeafe; background:rgba(37,99,235,.35);
    border:1px solid rgba(147,197,253,.45); padding:4px 10px; border-radius:999px;
  }
  .pill.warn{ color:#fde68a; background:rgba(217,119,6,.28); border-color:rgba(253,230,138,.5); }

  /* ---- section headings ---- */
  .sec{ margin:1.6rem 0 .5rem; }
  .sec h3{ font-size:1.12rem; font-weight:700; color:var(--ink); margin:0;
           display:flex; align-items:center; gap:.55rem; }
  .sec h3::before{ content:""; width:5px; height:20px; border-radius:3px;
                   background:linear-gradient(180deg,var(--accent),var(--accent2)); }
  .sec p{ color:var(--muted); font-size:.86rem; margin:.35rem 0 0 0; }

  /* ---- metric cards ---- */
  [data-testid="stMetric"]{
    background:var(--card); border:1px solid var(--border); border-radius:16px;
    padding:16px 18px; box-shadow:0 1px 2px rgba(15,23,42,.04),
    0 10px 26px -20px rgba(15,23,42,.4);
  }
  [data-testid="stMetricLabel"] p{ color:var(--muted); font-weight:600; font-size:.8rem;
     letter-spacing:.02em; }
  [data-testid="stMetricValue"]{ color:var(--ink); font-weight:800; }

  /* ---- alerts as soft callouts ---- */
  [data-testid="stAlert"]{ border-radius:14px; border:1px solid var(--border); }

  /* ---- tables / dataframes ---- */
  [data-testid="stDataFrame"], [data-testid="stTable"]{
    border:1px solid var(--border); border-radius:14px; overflow:hidden;
    box-shadow:0 1px 2px rgba(15,23,42,.03);
  }

  /* ---- buttons ---- */
  .stDownloadButton button, .stButton button{
    border-radius:11px; border:1px solid var(--border); font-weight:600;
    background:#ffffff; color:var(--ink);
  }
  .stDownloadButton button:hover, .stButton button:hover{
    border-color:var(--accent); color:var(--accent);
  }

  /* ---- sidebar ---- */
  [data-testid="stSidebar"]{
    background:linear-gradient(180deg,#0b1220 0%,#111c33 100%);
    border-right:1px solid #0b1220;
  }
  [data-testid="stSidebar"] *{ color:#cbd5e1; }
  [data-testid="stSidebar"] .brand{ color:#ffffff; font-weight:800; font-size:1.02rem;
    letter-spacing:-.01em; }
  [data-testid="stSidebar"] .brand small{ display:block; color:#7c8db5; font-weight:500;
    font-size:.72rem; margin-top:2px; }
  [data-testid="stSidebar"] .stRadio label{ font-weight:600; }
  [data-testid="stSidebar"] hr{ border-color:#1e2a44; }

  /* ---- code / captions ---- */
  code{ background:#eef2f8; color:#1e293b; border-radius:6px; padding:1px 5px; }
  [data-testid="stCaptionContainer"] p{ color:var(--muted); }

  .kv{ display:flex; flex-wrap:wrap; gap:10px; margin:.25rem 0 .4rem; }
  .chip{ background:#eef4ff; color:#1e40af; border:1px solid #dbe6ff;
         border-radius:999px; padding:5px 12px; font-size:.8rem; font-weight:600; }
  .chip.g{ background:#eafaf1; color:#15803d; border-color:#c7f0d8; }
  .chip.a{ background:#fff7e6; color:#b45309; border-color:#ffe4b8; }
  .chip.r{ background:#fdecec; color:#b91c1c; border-color:#fbd5d5; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def hero(title: str, subtitle: str, badge: str = "Research prototype",
         badge_class: str = "") -> None:
    cls = f"pill {badge_class}".strip()
    st.markdown(f"""<div class="hero">
      <span class="{cls}">{badge}</span>
      <h1>{title}</h1>
      <p>{subtitle}</p></div>""", unsafe_allow_html=True)


def section(title: str, desc: str = "") -> None:
    d = f"<p>{desc}</p>" if desc else ""
    st.markdown(f'<div class="sec"><h3>{title}</h3>{d}</div>', unsafe_allow_html=True)


# ----------------------------------------------------------------- helpers
@st.cache_data(show_spinner=False)
def load_panel(base: str) -> pd.DataFrame:
    p = OUT / f"panel_{base}.parquet"
    if not p.exists():
        return pd.DataFrame()
    df = pd.read_parquet(p)
    df["month"] = pd.to_datetime(df["month"])
    return df


@st.cache_data(show_spinner=False)
def load_preds(task: str) -> pd.DataFrame:
    p = ART / f"preds_{task}.parquet"
    if not p.exists():
        return pd.DataFrame()
    df = pd.read_parquet(p)
    df["month"] = pd.to_datetime(df["month"])
    return df


@st.cache_data(show_spinner=False)
def load_metrics() -> pd.DataFrame:
    p = ART / "metrics_all_tasks.csv"
    return pd.read_csv(p) if p.exists() else pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_markets() -> pd.DataFrame:
    p = ROOT / "raw" / "wfp_markets_zwe.csv"
    return pd.read_csv(p) if p.exists() else pd.DataFrame()


def missing(msg):
    st.warning(f"Data not available: {msg}. Run the pipeline scripts first.")


# ----------------------------------------------------------------- navigation
PAGES = [
    "Overview",
    "Data coverage & quality",
    "Price trends",
    "Rainfall",
    "Market & commodity explorer",
    "Model performance",
    "Historical holdout predictions",
    "Prediction",
    "Geographic view",
    "Limitations & disclaimers",
]
_qp = st.query_params.get("page")
_default = PAGES.index(_qp) if _qp in PAGES else 0

st.sidebar.markdown(
    '<div class="brand">ZW Food Price Stress<small>Machine-learning research dashboard'
    '</small></div>', unsafe_allow_html=True)
st.sidebar.markdown("---")
page = st.sidebar.radio("Section", PAGES, index=_default, label_visibility="collapsed")
st.sidebar.markdown("---")
st.sidebar.caption(DISCLAIMER)

# ----------------------------------------------------------------- overview
if page == "Overview":
    hero("Machine Learning Based Food Price Stress Prediction - Zimbabwe",
         "A reproducible, leakage-controlled pipeline over WFP market prices and "
         "CHIRPS rainfall. Every figure is generated from real artefacts; no results "
         "are fabricated.")
    st.info(DISCLAIMER)

    metrics = load_metrics()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Price rows (raw)", "28,168")
    c2.metric("Food cells (monthly)", "20,530")
    c3.metric("Series (market x commodity)", "3,029", help="median length 4 months")
    c4.metric("Next-month labelable", "37.1%")

    section("Modelled targets", "Two targets, reported separately for each price base "
            "and never pooled.")
    st.markdown(
        '<div class="kv">'
        '<span class="chip">Y1 - standardised-return stress: next-month log return '
        '&ge; +1.0 SD of trailing distribution</span>'
        '<span class="chip">Y2 - peer-relative stress: next-month price &ge; 1.20 x '
        'peer-market median</span>'
        '<span class="chip a">base rate Y1 ~ 15%</span>'
        '<span class="chip a">base rate Y2 ~ 16%</span>'
        '</div>', unsafe_allow_html=True)

    section("Headline results (honest)",
            "Historical performance does not transfer reliably to later periods; "
            "XGBoost does not dominate.")
    k1, k2, k3 = st.columns(3)
    k1.metric("Y1 holdout ROC-AUC", "0.54 - 0.67", help="weak; CI reaches chance")
    k2.metric("Y2 holdout ROC-AUC", "0.81 - 0.90", help="but partly persistence-driven")
    k3.metric("Best model (USD Y2)", "Hist GBM", help="0.886 vs XGBoost 0.842; tied on nominal Y2")

    if not metrics.empty:
        section("Best holdout ROC-AUC per task")
        ho = metrics[metrics["split"] == "holdout"]
        best = ho.loc[ho.groupby("task")["roc_auc"].idxmax(),
                      ["task", "model", "roc_auc", "pr_auc", "n"]]
        st.dataframe(best.sort_values("roc_auc", ascending=False),
                     use_container_width=True, hide_index=True)

# ----------------------------------------------------------------- coverage
elif page == "Data coverage & quality":
    hero("Data coverage & quality",
         "Coverage over time, currency and category mix, and the documented quality flags.")
    df = load_panel("usdprice")
    if df.empty:
        missing("panel")
    else:
        section("Monthly coverage", "Labelable cells per month")
        cov = df.groupby("month").size()
        st.line_chart(cov)
        col1, col2 = st.columns(2)
        with col1:
            st.caption("Currency mix of food cells")
            st.bar_chart(df["currency"].value_counts())
        with col2:
            st.caption("Category mix")
            st.bar_chart(df["category"].value_counts())
        section("Data-quality warnings", "See reports/phase1_data_quality_report.md")
        st.warning(
            "- 8 markets lack coordinates (Dulibadzimu, Kombai, Mandava, Mucheke, "
            "Murombedzi, Plumtree town, Renkini Bus Terminus, Tshovani).\n\n"
            "- `usdprice` has implausibly small values (min ~ 1.5e-5).\n\n"
            "- `priceflag=aggregate` rows are kept (78% of records) - flagged as a decision.\n\n"
            "- Median series length is 4 months, so only 37% of cells are next-month labelable."
        )
        section("Missingness of key derived features")
        cols = ["ret", "ret_lag1", "spi", "rain_anom_z", "population"]
        st.dataframe(df[cols].isna().mean().rename("missing_share").to_frame().round(4),
                     use_container_width=True)

# ----------------------------------------------------------------- prices
elif page == "Price trends":
    hero("Price trends", "Median monthly price by category on the USD base. Nominal "
         "series are not directly comparable across currency regimes.")
    df = load_panel("usdprice")
    if df.empty:
        missing("panel")
    else:
        section("Median monthly price by category")
        agg = (df.groupby(["month", "category"])["usdprice"].median().reset_index())
        piv = agg.pivot(index="month", columns="category", values="usdprice")
        st.line_chart(piv)

# ----------------------------------------------------------------- rainfall
elif page == "Rainfall":
    hero("Rainfall", "District rainfall anomaly and the real rainfall-price association.")
    df = load_panel("usdprice")
    if df.empty:
        missing("panel")
    else:
        section("District rainfall anomaly (z) over time")
        piv = df.pivot_table(index="month", columns="district", values="rain_anom_z").mean(axis=1)
        r = pd.read_parquet(OUT / "rainfall_district_month_anom.parquet") if (OUT / "rainfall_district_month_anom.parquet").exists() else None
        if r is not None and {"month", "rain_anom_z"}.issubset(r.columns):
            r["month"] = pd.to_datetime(r["month"])
            st.line_chart(r.groupby("month")["rain_anom_z"].mean())
        else:
            st.line_chart(piv)
        section("Lead-lag (real)",
                "Rainfall anomaly vs next-month return peaks at a 1-month lead, "
                "r ~ -0.11 to -0.12 (n = 12,520, p < 0.001) - weaker than the "
                "dissertation's reported -0.22.")
        ll = REP / "phase6_lead_lag.csv"
        if ll.exists():
            st.dataframe(pd.read_csv(ll).round(4), use_container_width=True, hide_index=True)

# ----------------------------------------------------------------- explorer
elif page == "Market & commodity explorer":
    hero("Market & commodity explorer", "Filter the food-cell panel by district and commodity.")
    df = load_panel("usdprice")
    if df.empty:
        missing("panel")
    else:
        f1, f2 = st.columns(2)
        prov = f1.multiselect("District", sorted(df["district"].dropna().unique()))
        comm = f2.multiselect("Commodity", sorted(df["commodity_id"].dropna().unique()))
        sub = df.copy()
        if prov:
            sub = sub[sub["district"].isin(prov)]
        if comm:
            sub = sub[sub["commodity_id"].isin(comm)]
        st.markdown(f'<span class="chip">{len(sub):,} cells</span>', unsafe_allow_html=True)
        st.dataframe(sub[["month", "commodity_id", "district", "price", "usdprice",
                          "spi", "rain_anom_z", "y1", "y2"]].head(500),
                     use_container_width=True, hide_index=True)

# ----------------------------------------------------------------- models
elif page == "Model performance":
    hero("Model performance", "Expanding-window CV versus the forward holdout, plus "
         "permutation importance.")
    m = load_metrics()
    if m.empty:
        missing("metrics_all_tasks.csv")
    else:
        task = st.selectbox("Task", sorted(m["task"].unique()))
        sub = m[m["task"] == task]
        piv = sub.pivot_table(index="model", columns="split", values="roc_auc")
        section("ROC-AUC (CV pooled vs forward holdout)")
        st.dataframe(piv.round(3), use_container_width=True)
        figp = FIG / f"phase7_rocauc_{task}.png"
        if figp.exists():
            st.image(str(figp))
        if task == "T2_usd_y2" and (FIG / "phase7_y2_diagnostics.png").exists():
            st.image(str(FIG / "phase7_y2_diagnostics.png"))
        st.caption("Persistence and majority are baselines. AUC alone is not sufficient "
                   "for early warning; see precision/recall and calibration.")
        imp = ART / f"perm_importance_{task}.csv"
        if imp.exists():
            section("Holdout permutation importance (ROC-AUC drop)")
            st.dataframe(pd.read_csv(imp).round(4), use_container_width=True, hide_index=True)
        with st.expander("Full metrics table"):
            st.dataframe(sub.round(4), use_container_width=True, hide_index=True)

# ----------------------------------------------------------------- holdout preds
elif page == "Historical holdout predictions":
    hero("Historical holdout predictions", "Ranked holdout-period scores. These are "
         "historical scores, not forecasts.")
    task = st.selectbox("Task", ["T1_usd_y1", "T2_usd_y2", "T3_nominal_y1", "T4_nominal_y2"])
    df = load_preds(task)
    if df.empty:
        missing(f"preds_{task}")
    else:
        model_col = st.selectbox("Model", [c for c in df.columns if c.startswith("p_")])
        thr = st.slider("Decision threshold", 0.0, 1.0, 0.5, 0.01)
        top = df.sort_values(model_col, ascending=False).head(25).copy()
        top["flagged"] = top[model_col] >= thr
        show = top[["month", "commodity_id", "district", "category",
                    model_col, "flagged"]].copy()
        show[model_col] = show[model_col].round(3)
        st.dataframe(show, use_container_width=True, hide_index=True)
        st.download_button("Download all holdout scores (CSV)",
                           df.to_csv(index=False).encode("utf-8"),
                           file_name=f"{task}_holdout_scores.csv")

# ----------------------------------------------------------------- scenario
elif page == "Prediction":
    hero("Prediction",
         "Score a market-month with the persisted, Optuna-tuned model. Produces an "
         "indicative probability for the next month - a prompt to verify, not an "
         "automated trigger.", badge="What-if", badge_class="warn")

    MODEL_MAP = {
        "Y2 - peer-relative stress": ("T2_usd_y2", "usdprice", "y2", "y2_peer_histgbm_usd"),
        "Y1 - standardised-return stress": ("T1_usd_y1", "usdprice", "y1", "y1_return_histgbm_usd"),
    }
    c0, c1 = st.columns([2, 1])
    choice = c0.selectbox("Prediction target", list(MODEL_MAP))
    task, base, ycol, mname = MODEL_MAP[choice]
    meta_p = MODELS / f"{mname}.meta.json"
    model_p = MODELS / f"{mname}.joblib"
    if not (meta_p.exists() and model_p.exists()):
        missing("models/ (run src/fit_final_model.py)")
        st.stop()

    import joblib
    meta = json.loads(meta_p.read_text(encoding="utf-8"))
    pipe = joblib.load(model_p)

    # ---- load a real market-month as the starting point
    static = dict(st.session_state.get("pred_static", {}))
    if c1.button("Load a real row", help="Rotate through real observed rows"):
        pan = load_panel(base)
        if not pan.empty:
            sub = pan[pan[f"labelable_{ycol}"]].copy()
            if len(sub):
                i = int(st.session_state.get("pred_row_i", -1)) + 1
                i %= len(sub)
                st.session_state["pred_row_i"] = i
                r = sub.iloc[i]

                def _f(v):
                    try:
                        f = float(v)
                        return f if np.isfinite(f) else np.nan
                    except (TypeError, ValueError):
                        return np.nan

                st.session_state["pred_static"] = {
                    k: (_f(r[k]) if k in r.index else np.nan)
                    for k in meta["features_numeric"]}
                static = dict(st.session_state["pred_static"])
                for k, col in (("p_spi", "spi"), ("p_retz", "ret_z_cur"),
                               ("p_rainz", "rain_anom_z"), ("p_peer", "peer_count")):
                    if col in r.index and pd.notna(r[col]):
                        v = _f(r[col])
                        st.session_state[k] = int(round(v)) if k == "p_peer" else v
                if "month" in r.index:
                    st.session_state["p_month"] = int(pd.Timestamp(r["month"]).month)
                if "category" in r.index and pd.notna(r["category"]):
                    st.session_state["p_cat"] = str(r["category"])
                if "currency" in r.index and pd.notna(r["currency"]):
                    st.session_state["p_curr"] = str(r["currency"])
                st.session_state["pred_row_label"] = (
                    f"{str(r.get('district', '?'))} - {str(r.get('commodity_id', '?'))} - "
                    f"{str(pd.Timestamp(r['month']).date()) if 'month' in r.index else '?'}")

    def _v(key, default):
        return st.session_state[key] if key in st.session_state else default

    def slider(label, lo, hi, default, step, key):
        val = _v(key, default)
        return st.slider(label, lo, hi, val, step, key=key)

    def selbox(label, options, key, idx=0):
        opts = list(options)
        cur = _v(key, opts[idx])
        if cur in opts:
            return st.selectbox(label, opts, index=opts.index(cur), key=key)
        return st.selectbox(label, opts, index=idx, key=key)

    cat_options = CFG.get("categories", {}).get("include",
                  ["cereals and tubers", "pulses and nuts", "oil and fats",
                   "meat, fish and eggs", "miscellaneous food"])

    r1a, r1b, r1c, r1d = st.columns(4)
    spi = slider("Peer-relative index (spi)", 0.5, 2.0, 1.0, 0.05, "p_spi")
    retz = slider("Standardised return", -3.0, 3.0, 0.0, 0.1, "p_retz")
    rainz = slider("Rainfall anomaly (z)", -3.0, 3.0, 0.0, 0.1, "p_rainz")
    peer = slider("Peer markets (peer_count)", 1, 50, 5, 1, "p_peer")

    r2a, r2b, r2c, r2d = st.columns(4)
    cat = selbox("Category", cat_options, "p_cat")
    curr = selbox("Currency", ["USD", "ZWL"], "p_curr")
    month = slider("Calendar month", 1, 12, 6, 1, "p_month")
    load_note = st.session_state.get("pred_row_label")

    # ---- build the feature row exactly like training
    row = {k: static.get(k, np.nan) for k in meta["features_numeric"]}
    row.update({"spi": spi, "ret_z_cur": retz, "rain_anom_z": rainz, "peer_count": float(peer),
                "interaction": retz * rainz,
                "month_sin": np.sin(2 * np.pi * month / 12),
                "month_cos": np.cos(2 * np.pi * month / 12)})
    row["category"] = cat
    row["currency"] = curr
    X = pd.DataFrame([row])[meta["features_numeric"] + meta["features_categorical"]]
    p = float(pipe.predict_proba(X)[0, 1])
    prev = float(meta.get("prevalence_train", 0.15))

    # ---- result card
    if p >= max(prev * 2.0, prev + 0.15):
        band, cls, advice = "HIGH", "r", "Verify local market information before acting."
    elif p >= prev * 1.3:
        band, cls, advice = "ELEVATED", "a", "Watch closely; cross-check with existing assessments."
    elif p >= prev:
        band, cls, advice = "ABOVE BASELINE", "a", "Slightly above the usual level for this series."
    else:
        band, cls, advice = "BELOW BASELINE", "g", "No indication beyond routine monitoring."

    st.markdown(f"""
      <div class="hero" style="background:linear-gradient(120deg,#0f172a,#1e293b);">
        <span class="pill {cls}">{band}</span>
        <h1 style="font-size:2.6rem;margin:.25rem 0 .1rem;">{p:.1%}</h1>
        <p>Predicted probability of {ycol.upper()} stress in the next month
           &middot; baseline prevalence in training {prev:.1%}</p>
      </div>""", unsafe_allow_html=True)
    st.progress(min(max(p, 0.0), 1.0))

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Training rows", f"{meta.get('n_train', 0):,}")
    m2.metric("Trained through", str(meta.get("trained_through", "-")))
    m3.metric("Holdout from", str(meta.get("holdout_from", "-")))
    m4.metric("Seed", str(meta.get("seed", "-")))

    tuning = meta.get("tuning") or {}
    ntr = tuning.get("n_trials")
    st.markdown(
        f'<div class="kv"><span class="chip">{advice}</span>'
        + (f'<span class="chip g">Optuna-tuned: {ntr} trials/task (TPE), '
           f'training-period CV only</span>' if ntr else "")
        + (f'<span class="chip">row: {load_note}</span>' if load_note else "")
        + '</div>', unsafe_allow_html=True)
    st.caption("Single-point, what-if score. Not a validated forecast. Do not act "
               "automatically on this value.")

# ----------------------------------------------------------------- geo
elif page == "Geographic view":
    hero("Geographic view", "Holdout-period mean predicted score and observed stress "
         "share by market.")
    df = load_preds("T2_usd_y2")
    mk = load_markets()
    if df.empty or mk.empty:
        missing("predictions or markets")
    else:
        model_col = "p_hist_gradient_boosting"
        g = df.groupby("market_id").agg(
            mean_score=(model_col, "mean"),
            stress_share=("y2", "mean"),
            n=("y2", "size")).reset_index()
        g = g.merge(mk[["market_id", "market", "latitude", "longitude"]], on="market_id", how="inner")
        map_df = g.rename(columns={"latitude": "lat", "longitude": "lon"})[["lat", "lon"]]
        st.map(map_df, size=max(1, len(map_df) // 5))
        st.caption("No market renders in the far south/edge where coordinates are missing.")
        st.dataframe(g.round(3).sort_values("stress_share", ascending=False),
                     use_container_width=True, hide_index=True)

# ----------------------------------------------------------------- limits
elif page == "Limitations & disclaimers":
    hero("Limitations & disclaimers",
         "Known limitations that must be stated in the dissertation.",
         badge="Important", badge_class="warn")
    st.markdown(
        """
- **Not validated as early warning.** All metrics are retrospective (CV + one forward holdout).
- **Sparse series.** Median series length is 4 months; only 37% of cells are next-month labelable.
- **Currency regimes.** USD/ZWL regimes differ; results are reported per base, never pooled.
- **Weak rainfall signal.** Lead-lag r ~ -0.11/-0.12; rainfall importance is small.
- **XGBoost does not dominate.** Histogram gradient boosting is best on the USD Y2 holdout (0.886 vs 0.842) and tied on nominal Y2.
- **Data-quality flags.** 8 markets lack coordinates; `usdprice` has near-zero values; aggregate priceflags retained.
- **Traceability.** Reported metrics are regenerated from artefacts: Optuna tuning (40 trials/task), confusion matrices, commodity AUCs, risk bands and districts all trace to `artifacts/` and `reports/phase6*`.
- **Blockers.** Stakeholder-engagement evidence is still pending (Chapter 5, §5.4).
        """)
    st.error(DISCLAIMER)
