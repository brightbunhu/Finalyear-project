"""Prediction Studio — score intuitive human inputs, technical features, or a CSV batch."""
from __future__ import annotations

import io
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import streamlit as st

from components import layout as L
from components import charts as C
from components import filters as CF
from utils import loaders as D
from utils import formatting as F

MODELS = {
    "Y2 — peer-relative stress (Spatial SPI >= 1.20)": "y2_peer_histgbm_usd",
    "Y1 — standardised-return stress (Return Surge >= 1.0 SD)": "y1_return_histgbm_usd",
}
ID_COLS = ["market_id", "commodity_id", "month", "district"]

COMMODITY_CONFIG = {
    "Maize (grain)": {
        "id": 51, "category": "cereals and tubers",
        "default_price": 0.55, "prev_price": 0.45, "peer_price": 0.46, "unit": "$ / kg"
    },
    "Maize meal (roller)": {
        "id": 264, "category": "cereals and tubers",
        "default_price": 0.70, "prev_price": 0.60, "peer_price": 0.62, "unit": "$ / kg"
    },
    "Oil (vegetable)": {
        "id": 96, "category": "oil and fats",
        "default_price": 2.50, "prev_price": 2.20, "peer_price": 2.25, "unit": "$ / L"
    },
    "Beans (sugar)": {
        "id": 432, "category": "pulses and nuts",
        "default_price": 2.80, "prev_price": 2.40, "peer_price": 2.45, "unit": "$ / kg"
    },
    "Rice": {
        "id": 52, "category": "cereals and tubers",
        "default_price": 1.40, "prev_price": 1.25, "peer_price": 1.28, "unit": "$ / kg"
    },
    "Wheat flour": {
        "id": 185, "category": "cereals and tubers",
        "default_price": 1.30, "prev_price": 1.15, "peer_price": 1.18, "unit": "$ / kg"
    },
    "Sugar": {
        "id": 97, "category": "miscellaneous food",
        "default_price": 1.50, "prev_price": 1.35, "peer_price": 1.38, "unit": "$ / kg"
    },
    "Fish (kapenta)": {
        "id": 887, "category": "meat, fish and eggs",
        "default_price": 4.50, "prev_price": 4.00, "peer_price": 4.10, "unit": "$ / kg"
    },
}


def _month_add(d: datetime, months: int) -> datetime:
    m = d.month - 1 + months
    y = d.year + m // 12
    mo = m % 12 + 1
    return d.replace(year=y, month=mo, day=1)

WEATHER_CONDITIONS = {
    "Severe Drought / Rain Failure (Major moisture deficit)": {
        "rain_anom_z": -1.85, "rain_anom_lag1": -1.60, "rain_anom_lag2": -1.20,
        "rain_anom_lag3": -0.90, "rain_roll3_mm": 20.0,
        "desc": "Severe rainfall deficit (-1.85 SD) characteristic of an El Niño drought shock."
    },
    "Below Normal Rainfall (Mild to moderate moisture stress)": {
        "rain_anom_z": -0.85, "rain_anom_lag1": -0.70, "rain_anom_lag2": -0.50,
        "rain_anom_lag3": -0.30, "rain_roll3_mm": 55.0,
        "desc": "Below-average precipitation (-0.85 SD) indicating dry spells during grain filling."
    },
    "Normal Seasonal Rainfall (Average meteorological baseline)": {
        "rain_anom_z": 0.05, "rain_anom_lag1": 0.00, "rain_anom_lag2": 0.00,
        "rain_anom_lag3": 0.00, "rain_roll3_mm": 95.0,
        "desc": "Precipitation within historical climatological norm (1981–2015 average)."
    },
    "Above Normal / Abundant Rain (Favourable surplus conditions)": {
        "rain_anom_z": 1.35, "rain_anom_lag1": 1.10, "rain_anom_lag2": 0.80,
        "rain_anom_lag3": 0.50, "rain_roll3_mm": 165.0,
        "desc": "Above-average rainfall (+1.35 SD) supporting robust staple grain yields."
    },
}

DEFAULT_DISTRICTS = [
    "Harare", "Bulawayo", "Bikita", "Mutare", "Mwenezi", "Mudzi", "Rushinga",
    "Chiredzi", "Bindura", "Gweru Urban", "Hwange", "Kariba", "Masvingo",
    "Chipinge", "Beitbridge", "Mount Darwin", "Hurungwe", "Buhera", "Gokwe South"
]


def _feature_schema(meta: dict) -> tuple[list[str], list[str]]:
    return list(meta.get("features_numeric", [])), list(meta.get("features_categorical", []))


def _holdout_auc(task: str, model: str = "hist_gradient_boosting") -> str:
    """Read the real forward-holdout ROC-AUC from the metrics artefact."""
    try:
        metrics = D.load_metrics()
        row = metrics[(metrics["task"] == task) & (metrics["split"] == "holdout")
                      & (metrics["model"] == model)]
        if row.empty:
            return "Not available"
        return f"{float(row.iloc[0]['roc_auc']):.4f}"
    except Exception:
        return "Not available"
COMMODITY_SANITY_BOUNDS_USD = {
    "Maize (grain)": {"min": 0.05, "max": 4.00, "extreme": 10.00},
    "Maize meal (roller)": {"min": 0.10, "max": 5.00, "extreme": 12.00},
    "Oil (vegetable)": {"min": 0.50, "max": 8.00, "extreme": 16.00},
    "Beans (sugar)": {"min": 0.50, "max": 8.00, "extreme": 18.00},
    "Rice": {"min": 0.30, "max": 6.00, "extreme": 12.00},
    "Wheat flour": {"min": 0.30, "max": 6.00, "extreme": 12.00},
    "Sugar": {"min": 0.30, "max": 6.00, "extreme": 12.00},
    "Fish (kapenta)": {"min": 1.00, "max": 20.00, "extreme": 40.00},
}


@st.cache_data(show_spinner=False)
def _load_district_market_mapping() -> dict[str, list[dict]]:
    """Return dictionary mapping district names to real markets from crosswalk."""
    crosswalk_path = Path(__file__).resolve().parents[2] / "data_processed" / "market_admin_crosswalk.csv"
    if not crosswalk_path.exists():
        return {}
    try:
        cw = pd.read_csv(crosswalk_path)
        d_map: dict[str, list[dict]] = {}
        for _, r in cw.iterrows():
            d = str(r["district_geo"] if pd.notna(r.get("district_geo")) else r["admin2"]).strip()
            m = str(r["market"]).strip()
            mid = int(r["market_id"]) if pd.notna(r.get("market_id")) else 0
            if d and d != "nan" and m and m != "nan":
                d_map.setdefault(d, []).append({"name": m, "id": mid})
        return d_map
    except Exception:
        return {}


def _get_district_markets(district: str, d_map: dict[str, list[dict]]) -> list[dict]:
    """Retrieve markets specifically located in the selected district."""
    if district in d_map:
        return d_map[district]
    norm = district.lower().replace(" urban", "").replace(" rural", "").strip()
    for k, v in d_map.items():
        knorm = k.lower().replace(" urban", "").replace(" rural", "").strip()
        if norm == knorm:
            return v
    for k, v in d_map.items():
        if norm in k.lower() or k.lower() in norm:
            return v
    return []

def _user_friendly_calculator(meta: dict, target_key: str) -> None:
    """Time-aware calculator to predict next-month stress."""
    st.caption("Predict stress for **next month (t+1)** using prices observed up to month **t**. "
               "Use the button to pull a real example from the panel, or enter your own values.")

    panel = D.load_panel("usdprice")
    districts = sorted(panel["district"].dropna().unique().tolist()) if not panel.empty else DEFAULT_DISTRICTS
    geo = D.load_geo()
    if geo and "features" in geo:
        geo_districts = sorted({f["properties"]["shapeName"] for f in geo["features"]})
        if geo_districts:
            districts = geo_districts

    with st.container(border=True):
        st.markdown("**1) Market & Commodity**")
        c1, c2, c3, c4 = st.columns([1.2, 1.0, 1.2, 0.8])
        dist_default = "Harare" if "Harare" in districts else districts[0]
        district = c1.selectbox("District", districts,
                                index=districts.index(dist_default) if dist_default in districts else 0,
                                key="uf_district")
        market_name = c2.text_input("Market (optional)", value=f"{district} Main Market", key="uf_market")
        commodity_label = c3.selectbox("Commodity", list(COMMODITY_CONFIG.keys()), index=0, key="uf_commodity")
        comm_info = COMMODITY_CONFIG[commodity_label]
        currency = c4.selectbox("Currency", ["USD", "ZWL"], index=0, key="uf_currency")

    now = datetime.now()
    default_obs = datetime(now.year, now.month, 1)
    obs_years = list(range(now.year - 6, now.year + 1))

    with st.container(border=True):
        st.markdown("**2) Price Information**")
        t1, t2, t3 = st.columns([0.8, 0.8, 1.6])
        obs_year = t1.selectbox("Year", obs_years,
                                index=obs_years.index(default_obs.year) if default_obs.year in obs_years else 0,
                                key="uf_obs_year")
        obs_month = t2.selectbox("Month", list(range(1, 13)), index=default_obs.month - 1, key="uf_obs_month")
        obs_month_dt = datetime(obs_year, obs_month, 1)
        target_month_dt = _month_add(obs_month_dt, 1)
        prev_month_dt = _month_add(obs_month_dt, -1)
        two_month_dt = _month_add(obs_month_dt, -2)
        three_month_dt = _month_add(obs_month_dt, -3)
        t3.info(f"Observed prices up to **{obs_month_dt:%Y-%m}** → Predicting for **{target_month_dt:%Y-%m}** (next month)")

        if st.button("Use latest real example for this district/commodity", use_container_width=False, key="uf_load_example"):
            dfp = D.load_panel("usdprice")
            if dfp is not None and not dfp.empty:
                cand = dfp[(dfp["district"] == district) &
                           (dfp["commodity_id"] == comm_info["id"]) &
                           (dfp["currency"] == "USD")].dropna(subset=["price"]).sort_values("month")
                if len(cand) >= 4:
                    take = cand.tail(4)
                    obs = pd.to_datetime(take["month"].iloc[-1]).to_pydatetime()
                    st.session_state["uf_obs_year"] = obs.year
                    st.session_state["uf_obs_month"] = obs.month
                    st.session_state["uf_currency"] = "USD"
                    st.session_state["uf_p_t"] = float(take["price"].iloc[-1])
                    st.session_state["uf_p_t1"] = float(take["price"].iloc[-2])
                    st.session_state["uf_p_t2"] = float(take["price"].iloc[-3])
                    st.session_state["uf_p_t3"] = float(take["price"].iloc[-4])
                    st.session_state["uf_p_peer"] = float(take["peer_median"].iloc[-1])
                    st.rerun()
                else:
                    st.warning("Not enough consecutive months for this selection. Enter prices manually below.")

        unit = comm_info["unit"]
        p1, p2, p3, p4 = st.columns(4)
        cur_price = p1.number_input(f"{obs_month_dt:%Y-%m} (t) {unit}", min_value=0.01, max_value=50000.0,
                                    value=comm_info["default_price"], step=0.05, format="%.2f", key="uf_p_t")
        prev_price = p2.number_input(f"{prev_month_dt:%Y-%m} (t-1) {unit}", min_value=0.01, max_value=50000.0,
                                     value=comm_info["prev_price"], step=0.05, format="%.2f", key="uf_p_t1")
        price_m2 = p3.number_input(f"{two_month_dt:%Y-%m} (t-2) {unit}", min_value=0.01, max_value=50000.0,
                                    value=comm_info["prev_price"], step=0.05, format="%.2f", key="uf_p_t2")
        price_m3 = p4.number_input(f"{three_month_dt:%Y-%m} (t-3) {unit}", min_value=0.01, max_value=50000.0,
                                    value=comm_info["prev_price"], step=0.05, format="%.2f", key="uf_p_t3")

    with st.container(border=True):
        st.markdown("**3) Time & Features**")
        q1, q2 = st.columns([1, 1])
        peer_price = q1.number_input(f"National peer median ({obs_month_dt:%Y-%m}) {unit}", min_value=0.01, max_value=50000.0,
                                     value=comm_info["peer_price"], step=0.05, format="%.2f", key="uf_p_peer",
                                     help="Used for SPI = price_t / peer_median_t")
        weather_label = q2.selectbox("Moisture condition", list(WEATHER_CONDITIONS.keys()), index=0, key="uf_weather")
        st.caption(WEATHER_CONDITIONS[weather_label]['desc'])

    st.write("")
    if st.button("Run Prediction", type="primary", use_container_width=True, key="uf_submit"):
        ret_mom = (cur_price - prev_price) / prev_price if prev_price > 0 else 0.0
        ret_mom_m1m = (prev_price - price_m2) / price_m2 if price_m2 > 0 else ret_mom
        ret_mom_m2m = (price_m2 - price_m3) / price_m3 if price_m3 > 0 else ret_mom_m1m
        sigma_dist = 0.18
        mu_dist = 0.04
        ret_z_cur = (ret_mom - mu_dist) / sigma_dist
        ret_lag1 = ret_mom_m1m
        ret_lag2 = ret_mom_m2m
        ret_roll3 = (ret_mom + ret_lag1 + ret_lag2) / 3.0
        spi = cur_price / peer_price if peer_price > 0 else 1.0

        weather_info = WEATHER_CONDITIONS[weather_label]
        rain_anom_z = weather_info["rain_anom_z"]
        rain_anom_lag1 = weather_info["rain_anom_lag1"]
        rain_anom_lag2 = weather_info["rain_anom_lag2"]
        rain_anom_lag3 = weather_info["rain_anom_lag3"]
        rain_roll3_mm = weather_info["rain_roll3_mm"]
        interaction = ret_z_cur * rain_anom_z

        cur_month = target_month_dt.month
        month_sin = float(np.sin(2 * np.pi * cur_month / 12))
        month_cos = float(np.cos(2 * np.pi * cur_month / 12))
        log_pop = 11.75

        feature_row = {
            "ret_z_cur": ret_z_cur,
            "ret_lag1": ret_lag1,
            "ret_lag2": ret_lag2,
            "ret_roll3": ret_roll3,
            "spi": spi,
            "peer_count": 12.0,
            "rain_anom_z": rain_anom_z,
            "rain_anom_lag1": rain_anom_lag1,
            "rain_anom_lag2": rain_anom_lag2,
            "rain_anom_lag3": rain_anom_lag3,
            "rain_roll3_mm": rain_roll3_mm,
            "month_sin": month_sin,
            "month_cos": month_cos,
            "log_population": log_pop,
            "interaction": interaction,
            "category": comm_info["category"],
            "currency": currency,
        }

        pipe_y2, meta_y2 = D.load_model("y2_peer_histgbm_usd")
        pipe_y1, meta_y1 = D.load_model("y1_return_histgbm_usd")

        p_y2, p_y1 = None, None
        if pipe_y2 is not None and meta_y2 is not None:
            X2 = pd.DataFrame([feature_row])[meta_y2["features_numeric"] + meta_y2["features_categorical"]]
            p_y2 = float(pipe_y2.predict_proba(X2)[0, 1])

        if pipe_y1 is not None and meta_y1 is not None:
            X1 = pd.DataFrame([feature_row])[meta_y1["features_numeric"] + meta_y1["features_categorical"]]
            p_y1 = float(pipe_y1.predict_proba(X1)[0, 1])

        st.session_state["uf_calculated_results"] = {
            "district": district, "market": market_name, "commodity": commodity_label,
            "currency": currency, "cur_price": cur_price, "prev_price": prev_price,
            "peer_price": peer_price, "ret_mom": ret_mom, "ret_z_cur": ret_z_cur,
            "spi": spi, "rain_anom_z": rain_anom_z, "interaction": interaction,
            "p_y2": p_y2, "p_y1": p_y1, "prev_y2": (meta_y2 or {}).get("prevalence_train", 0.163),
            "prev_y1": (meta_y1 or {}).get("prevalence_train", 0.150),
            "feature_row": feature_row,
            "obs_month": obs_month_dt.strftime("%Y-%m"),
            "target_month": target_month_dt.strftime("%Y-%m"),
            "prev_month": prev_month_dt.strftime("%Y-%m"),
        }

    # Render results if available
    res = st.session_state.get("uf_calculated_results")
    if res:
        st.markdown("---")
        st.markdown("#### Stress assessment results")

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Observed MoM Change", f"{res['ret_mom']:+.1%}",
                  f"Z-Score: {res['ret_z_cur']:+.2f}σ", delta_color="inverse")
        k2.metric("Spatial Price Index (SPI)", f"{res['spi']:.2f}x",
                  f"{(res['spi']-1.0):+.1%} vs Peers", delta_color="inverse")
        k3.metric("Rainfall Anomaly", f"{res['rain_anom_z']:+.2f}σ",
                  "Deficit" if res['rain_anom_z'] < 0 else "Normal/Surplus")
        k4.metric("Climate-Price Interaction", f"{res['interaction']:+.2f}",
                  "Drought Amplifier" if res['interaction'] < 0 else "Neutral")

        # Risk scoring cards
        auc_y2 = _holdout_auc("T2_usd_y2")
        auc_y1 = _holdout_auc("T1_usd_y1")
        risk_col_map = {
            "very-high": L.THEME["risk_very_high"],
            "high": L.THEME["risk_high"],
            "med": L.THEME["risk_medium"],
            "low": L.THEME["risk_low"],
        }

        rc1, rc2 = st.columns(2)
        with rc1:
            py2 = res["p_y2"] if res["p_y2"] is not None else 0.0
            band_y2, cls_y2 = L.risk_badge(py2, res["prev_y2"])
            col_y2 = risk_col_map.get(cls_y2, L.THEME["primary_blue"])
            st.markdown(f"""
            <div class="card" style="border-left: 5px solid {col_y2};">
                <div class="metric-lbl">Target Y2: Spatial Price Stress (SPI ≥ 1.20)</div>
                <div class="metric-val" style="font-size:32px;">{py2:.1%} Probability</div>
                <div style="margin: 8px 0;">{L.badge(band_y2, cls_y2)}</div>
                <div class="metric-cap">Baseline historical prevalence: {res['prev_y2']:.1%} · 12-Month Holdout ROC-AUC: <b>{auc_y2}</b></div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(min(max(py2, 0.0), 1.0))

        with rc2:
            py1 = res["p_y1"] if res["p_y1"] is not None else 0.0
            band_y1, cls_y1 = L.risk_badge(py1, res["prev_y1"])
            col_y1 = risk_col_map.get(cls_y1, L.THEME["primary_blue"])
            st.markdown(f"""
            <div class="card" style="border-left: 5px solid {col_y1};">
                <div class="metric-lbl">Target Y1: Return Surge Acceleration (≥ 1.0σ)</div>
                <div class="metric-val" style="font-size:32px;">{py1:.1%} Probability</div>
                <div style="margin: 8px 0;">{L.badge(band_y1, cls_y1)}</div>
                <div class="metric-cap">Baseline historical prevalence: {res['prev_y1']:.1%} · 12-Month Holdout ROC-AUC: <b>{auc_y1}</b></div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(min(max(py1, 0.0), 1.0))

        # Plain-English Executive Summary
        st.write("")
        stress_level = "CRITICAL" if (py2 >= 0.40 or py1 >= 0.40) else "ELEVATED" if (py2 >= res["prev_y2"] or py1 >= res["prev_y1"]) else "STABLE"
        alert_box = st.error if stress_level == "CRITICAL" else st.warning if stress_level == "ELEVATED" else st.success

        direction_word = "higher" if res["ret_mom"] > 0 else "lower"
        spi_comparison = "exceeds" if res["spi"] >= 1.0 else "is below"
        obs_m = res.get("obs_month", "?")
        tmo = res.get("target_month", "?")
        pmo = res.get("prev_month", "?")

        summary_text = (
            f"**Early Warning Summary:** Using prices observed in **{obs_m}** for **{res['commodity']}** in **{res['district']}** "
            f"({res['currency']} {res['cur_price']:.2f} in {obs_m}, {res['prev_price']:.2f} in {pmo}), "
            f"the model predicts the probability of market stress for **{tmo}** (next month after the observation). "
            f"Month-over-month change from {pmo} to {obs_m} is **{abs(res['ret_mom']):.1%} {direction_word}**; "
            f"the price in {obs_m} {spi_comparison} the contemporaneous peer median by **{abs(res['spi'] - 1.0):.1%}** (SPI = {res['spi']:.2f}). "
            f"With a precipitation anomaly of **{res['rain_anom_z']:+.2f}σ**, the model estimates "
            f"a **{py2:.1%} probability of acute spatial price stress** (Y2) and **{py1:.1%} probability of continued price acceleration** (Y1) for **{tmo}**."
        )
        alert_box(summary_text)

        # Operational Interventions
        st.markdown("**Recommended actions**")
        rec1, rec2, rec3 = st.columns(3)
        with rec1:
            st.markdown("""
            **1. Field Market Verification**  
            - Dispatch enumerators to verify local grain availability and depot stocks in the district.  
            - Verify whether private millers or grain traders are rationing supplies.
            """)
        with rec2:
            st.markdown("""
            **2. Supply Routing & Grain Movement**  
            - If SPI ≥ 1.20, evaluate targeted grain transfer from nearest surplus Grain Marketing Board (GMB) depots.  
            - Inspect transport access along primary road corridors into the district.
            """)
        with rec3:
            st.markdown("""
            **3. Safety Net & Purchasing Power**  
            - If food stress probability exceeds baseline prevalence, adjust cash/voucher transfer values.  
            - Protect vulnerable households from purchasing power erosion.
            """)

        # Under the hood feature inspection for verification
        with st.expander("View computed feature vector"):
            st.caption("Here is the exact feature vector calculated and fed into the HistGradientBoostingClassifier:")
            st.dataframe(pd.DataFrame([res["feature_row"]]), use_container_width=True)


def _load_example(meta: dict, target: str) -> dict:
    panel = D.load_panel(meta.get("base", "usdprice"))
    if panel.empty:
        return {}
    lab = f"labelable_{target}"
    sub = panel[panel[lab]] if lab in panel.columns else panel
    if sub.empty:
        sub = panel
    r = sub.iloc[-1]
    nums = {}
    for c in meta["features_numeric"]:
        if c == "interaction":
            continue
        try:
            v = float(r[c]) if c in r.index else np.nan
        except (TypeError, ValueError):
            v = np.nan
        nums[c] = v if np.isfinite(v) else np.nan
    cats = {c: (r[c] if c in r.index else None) for c in meta["features_categorical"]}
    return {"numeric": nums, "categorical": cats,
            "context": {c: r[c] for c in ID_COLS if c in r.index}}


def _advanced_technical_inputs(meta: dict, target: str) -> None:
    nums, cats = _feature_schema(meta)
    prev = float(meta.get("prevalence_train", 0.15))

    st.markdown("**Direct feature inputs**")
    st.caption("Directly inspect and override raw normalized Z-scores, lag features, and rolling metrics:")

    if st.button("Load a real example from latest eligible panel month", key="ps_load_adv"):
        st.session_state["ps_example"] = _load_example(meta, target)
    ex = st.session_state.get("ps_example", {})

    ctx = ex.get("context", {})
    c1, c2, c3, c4 = st.columns(4)
    c1.text_input("District", value=str(ctx.get("district", "Bikita")), key="ps_district_adv")
    c2.text_input("Market ID", value=str(ctx.get("market_id", "1")), key="ps_market_adv")
    c3.text_input("Commodity ID", value=str(ctx.get("commodity_id", "51")), key="ps_commodity_adv")
    c4.text_input("Month", value=str(ctx.get("month", "2024-10-01"))[:10], key="ps_month_adv")

    price_fields = [c for c in nums if c in ("ret_z_cur", "ret_lag1", "ret_lag2", "ret_roll3", "spi", "peer_count")]
    rain_fields = [c for c in nums if c.startswith("rain")]
    other_fields = [c for c in nums if c not in price_fields + rain_fields]

    def _default(c):
        v = ex.get("numeric", {}).get(c, None)
        try:
            fv = float(v)
            return fv if np.isfinite(fv) else 0.0
        except (TypeError, ValueError):
            return 0.0

    values = {}
    st.markdown("**Price & Spatial Indicators**")
    cols = st.columns(min(3, len(price_fields)) or 1)
    for i, c in enumerate(price_fields):
        values[c] = cols[i % len(cols)].number_input(c, value=_default(c), format="%.4f", key=f"ps_adv_{c}")

    st.markdown("**Precipitation Indicators**")
    rcols = st.columns(min(3, len(rain_fields)) or 1)
    for i, c in enumerate(rain_fields):
        values[c] = rcols[i % len(rcols)].number_input(c, value=_default(c), format="%.4f", key=f"ps_adv_{c}")

    st.markdown("**Harmonic & Demographic Inputs**")
    ocols = st.columns(min(3, len(other_fields)) or 1)
    for i, c in enumerate(other_fields):
        values[c] = ocols[i % len(ocols)].number_input(c, value=_default(c), format="%.4f", key=f"ps_adv_{c}")

    cc1, cc2 = st.columns(2)
    cats_vals = {}
    ex_cats = ex.get("categorical", {})
    cat_opts = ["cereals and tubers", "oil and fats", "pulses and nuts", "meat, fish and eggs", "miscellaneous food"]
    for i, c in enumerate(cats):
        opts = cat_opts if c == "category" else ["USD", "ZWL"]
        default = ex_cats.get(c)
        idx = opts.index(default) if default in opts else 0
        cats_vals[c] = (cc1 if i == 0 else cc2).selectbox(c, opts, index=idx, key=f"ps_adv_cat_{c}")

    if st.button("Score Technical Features", type="primary", key="ps_score_adv"):
        pipe, _ = D.load_model(meta.get("name", ""))
        row = dict(values)
        row["interaction"] = row.get("ret_z_cur", 0.0) * row.get("rain_anom_z", 0.0)
        row.update(cats_vals)
        X = pd.DataFrame([row])[meta["features_numeric"] + meta["features_categorical"]]
        try:
            p = float(pipe.predict_proba(X)[0, 1])
            st.session_state["ps_adv_result"] = {
                "p": p, "prev": prev, "target": meta["target"],
                "name": meta.get("name"), "trained": meta.get("trained_through")
            }
        except Exception as exc:
            st.error(f"Scoring failed: {exc}")

    res_adv = st.session_state.get("ps_adv_result")
    if res_adv:
        st.write("")
        p = res_adv["p"]
        band, cls = L.risk_badge(p, res_adv["prev"])
        L.card(f'<div class="metric-lbl">{L.esc(res_adv["target"].upper())} Predicted Probability</div>'
               f'<div class="metric-val" style="font-size:32px">{p:.1%}</div>'
               f'{L.badge(band, cls)}'
               f'<div class="metric-cap">Baseline prevalence: {res_adv["prev"]:.1%} · Model: {res_adv["name"]}</div>')
        st.progress(min(max(p, 0.0), 1.0))


def _batch(meta: dict) -> None:
    nums, cats = _feature_schema(meta)
    template_cols = ID_COLS + nums + cats
    template = pd.DataFrame(columns=template_cols)
    st.download_button("Download CSV template",
                       template.to_csv(index=False).encode("utf-8"),
                       file_name=f"prediction_template_{meta.get('name','model')}.csv")
    st.caption(f"Required model columns: {', '.join(nums + cats)}.")

    up = st.file_uploader("Upload a CSV file for Batch Scoring", type=["csv"], key="ps_upload")
    if up is None:
        return
    try:
        raw = pd.read_csv(up)
    except Exception as exc:
        st.error(f"Could not read the CSV: {exc}")
        return

    missing = [c for c in nums + cats if c not in raw.columns]
    if missing:
        st.error(f"Missing required columns: {', '.join(missing)}.")
        return

    df = raw.copy()
    for c in nums:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    for c in cats:
        df[c] = df[c].astype("string")

    if "interaction" in nums and "ret_z_cur" in df.columns and "rain_anom_z" in df.columns:
        df["interaction"] = df["ret_z_cur"].fillna(0) * df["rain_anom_z"].fillna(0)

    pipe, _ = D.load_model(meta.get("name", ""))
    if pipe is None:
        L.unavailable("the model", f"models/{meta.get('name')}.joblib")
        return

    try:
        df["predicted_probability"] = pipe.predict_proba(df[nums + cats])[:, 1]
    except Exception as exc:
        st.error(f"Batch scoring failed: {exc}")
        return

    st.success(f"Successfully scored {len(df):,} rows! Mean Probability: {df['predicted_probability'].mean():.1%}")
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button("Download Scored Rows (CSV)",
                       df.to_csv(index=False).encode("utf-8"),
                       file_name="batch_scored_predictions.csv")


def _quality(meta: dict) -> None:
    nums, cats = _feature_schema(meta)
    st.markdown("**Input schema and feature registry**")
    st.caption(f"{len(nums)} numeric features and {len(cats)} categorical features in model pipeline:")
    st.dataframe(pd.DataFrame({
        "Role": ["Numeric"] * len(nums) + ["Categorical"] * len(cats),
        "Feature Name": nums + cats,
    }), use_container_width=True, hide_index=True)


def render() -> None:
    L.page_header("Next-Month Price Stress Prediction",
                  "Predict stress for the month after your last observation using prices, peer median and rainfall.",
                  provenance="models/*.joblib + models/*.meta.json (audited pipelines)")

    target_label = st.selectbox("Active Early Warning Model Target", list(MODELS), key="ps_target")
    name = MODELS[target_label]
    pipe, meta = D.load_model(name)
    if pipe is None or meta is None:
        L.unavailable(f"the model for {target_label}", f"models/{name}.joblib")
        return

    st.caption(f"Active model binary: `models/{name}.joblib` · Trained through: "
               f"**{F.month_label(meta.get('trained_through'))}** · "
               f"Training Prevalence: **{F.pct(meta.get('prevalence_train'))}**")

    tabs = st.tabs([
        "Next-month predictor",
        "Advanced mode (direct Z-scores)",
        "CSV batch prediction",
        "Input schema & feature quality"
    ])

    with tabs[0]:
        _user_friendly_calculator(meta, meta.get("target", "y2"))
    with tabs[1]:
        _advanced_technical_inputs(meta, meta.get("target", "y2"))
    with tabs[2]:
        _batch(meta)
    with tabs[3]:
        _quality(meta)

    st.caption(f"Note: {L.DISCLAIMER}")
