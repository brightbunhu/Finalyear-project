"""Statistical Analysis — exploratory statistics, distributions, trends, groups, correlations."""
from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from components import layout as L
from components import charts as C
from utils import loaders as D
from utils import statistics as S
from utils import formatting as F

DATASETS = {
    "Panel — USD (model-ready)": ("panel", "usdprice", "Model-ready panel (USD base)"),
    "Panel — Nominal within currency (model-ready)": ("panel", "nominal_within_currency",
                                                       "Model-ready panel (nominal base)"),
    "Rainfall district-month anomalies": ("rain_anom", None, "Processed rainfall features"),
    "Market–district crosswalk": ("crosswalk", None, "Merge artefact"),
}

# ID-like / non-meaningful continuous columns hidden from analysis by default
ID_COLS = {"market_id", "commodity_id", "n_records", "admin1", "admin2", "district_name_match"}
CANDIDATE_GROUPS = ["district", "province_geo", "category", "currency", "admin1", "cal_month_y",
                    "cal_month_x", "price_base"]


@st.cache_data(show_spinner=False)
def _load(kind: str, base: str | None) -> pd.DataFrame:
    if kind == "panel":
        return D.load_panel(base)
    if kind == "rain_anom":
        return D.load_rainfall_anom()
    if kind == "crosswalk":
        return D.load_crosswalk()
    return pd.DataFrame()


def _context(name: str, df: pd.DataFrame, prov: str) -> None:
    dcols = [c for c in ("month", "date") if c in df.columns]
    drange = F.date_range(df[dcols[0]]) if dcols else "Unavailable (no date column)"
    num_cols = df.select_dtypes("number").columns
    L.kpi_row([
        {"icon": "🗃️", "color": "#EFF6FF", "label": "Dataset", "value": name.split("—")[-1].strip()[:18],
         "caption": prov},
        {"icon": "▤", "color": "#F0FDF4", "label": "Dimensions",
         "value": f"{F.intc(len(df))} × {F.intc(df.shape[1])}", "caption": "rows × columns"},
        {"icon": "📅", "color": "#FEF9C3", "label": "Date range", "value": drange,
         "caption": "min → max"},
        {"icon": "🔢", "color": "#FDF2F8", "label": "Numeric variables",
         "value": F.intc(len(num_cols)), "caption": "available for analysis"},
    ])


def _filters(df: pd.DataFrame, name: str) -> pd.DataFrame:
    sub = df.copy()
    cols = st.columns(4)
    dcols = [c for c in ("month", "date") if c in df.columns]
    if dcols:
        d = pd.to_datetime(sub[dcols[0]], errors="coerce")
        valid = d.dropna()
        if not valid.empty:
            lo, hi = valid.min().date(), valid.max().date()
            rng = cols[0].date_input("Date range", value=(lo, hi), min_value=lo, max_value=hi,
                                     key=f"sa_date_{name}")
            if isinstance(rng, (list, tuple)) and len(rng) == 2:
                sub = sub[(d >= pd.Timestamp(rng[0])) & (d <= pd.Timestamp(rng[1]))]
    gi = 1
    for gcol in ("district", "category", "currency"):
        if gcol in sub.columns and gi < 4:
            opts = sorted(sub[gcol].dropna().astype(str).unique().tolist())
            sel = cols[gi].multiselect(gcol.capitalize(), opts, key=f"sa_{gcol}_{name}")
            if sel:
                sub = sub[sub[gcol].astype(str).isin(sel)]
            gi += 1
    extra = [c for c in ("commodity_id", "market_id") if c in sub.columns and sub[c].nunique(dropna=True) > 1]
    if extra:
        more = st.columns(len(extra))
        labels = {"commodity_id": "Commodity", "market_id": "Market"}
        for box, gcol in zip(more, extra):
            opts = sorted(sub[gcol].dropna().astype(str).unique().tolist())
            sel = box.multiselect(labels[gcol], opts, key=f"sa_{gcol}_{name}")
            if sel:
                sub = sub[sub[gcol].astype(str).isin(sel)]
    if st.button("Reset filters", key=f"sa_reset_{name}"):
        for k in list(st.session_state.keys()):
            if k.startswith(f"sa_") and k.endswith(name):
                del st.session_state[k]
        st.rerun()
    return sub


def render() -> None:
    L.page_header("Statistical Analysis",
                  "Explore distributions, summary statistics, temporal patterns and "
                  "relationships in the research data.",
                  provenance="Descriptive analysis of stored datasets — not model-performance measures.")

    ds_name = st.selectbox("Dataset", list(DATASETS), key="sa_dataset")
    kind, base, prov = DATASETS[ds_name]
    df = _load(kind, base)
    if df.empty:
        L.unavailable("the selected dataset", f"data_processed/*{base or kind}*")
        return

    with st.expander("Analysis context", expanded=True):
        _context(ds_name, df, prov)
        st.caption(f"Provenance: {prov}. All statistics below are computed on the "
                   "filtered observations and are not model-performance measures.")

    L.section("Filters", "All outputs below use the active filtered dataset.")
    sub = _filters(df, kind + (base or ""))
    st.caption(f"Active sample: {F.intc(len(sub))} of {F.intc(len(df))} rows · "
               f"{F.intc(sub.shape[1])} variables.")

    if sub.empty:
        st.warning("The filters produced an empty dataset. Widen the selection.")
        st.caption(f"Note: {L.DISCLAIMER}")
        return

    num_vars = [c for c in sub.select_dtypes("number").columns if c not in ID_COLS]
    group_vars = [c for c in CANDIDATE_GROUPS if c in sub.columns and
                  sub[c].nunique(dropna=True) > 1]

    if not num_vars:
        L.unavailable("numeric variables in this dataset")
        st.caption(f"Note: {L.DISCLAIMER}")
        return

    tabs = st.tabs(["Overview", "Distributions", "Trends over time", "Group comparisons",
                    "Correlations", "Missingness & quality", "Statistical tests"])

    # ---------------- Overview ----------------
    with tabs[0]:
        var = st.selectbox("Variable", num_vars, key="sa_ov_var")
        d = S.describe(sub[var])
        L.kpi_row([
            {"icon": "🔢", "color": "#EFF6FF", "label": "Non-missing", "value": F.intc(d["n"]),
             "caption": f"{F.intc(d['missing'])} missing"},
            {"icon": "➗", "color": "#F0FDF4", "label": "Mean", "value": F.num(d["mean"], 3)},
            {"icon": "📍", "color": "#FEF9C3", "label": "Median", "value": F.num(d["median"], 3)},
            {"icon": "📏", "color": "#FDF2F8", "label": "Std dev", "value": F.num(d["std"], 3)},
        ])
        L.kpi_row([
            {"icon": "⬇️", "color": "#EFF6FF", "label": "Min", "value": F.num(d["min"], 3)},
            {"icon": "⬆️", "color": "#F0FDF4", "label": "Max", "value": F.num(d["max"], 3)},
            {"icon": "📦", "color": "#FEF9C3", "label": "IQR",
             "value": F.num(d["iqr"], 3), "caption": f"Q1 {F.num(d['q1'],2)} · Q3 {F.num(d['q3'],2)}"},
            {"icon": "📐", "color": "#FDF2F8", "label": "Skew / Kurt",
             "value": f"{F.num(d['skew'],2)} / {F.num(d['kurtosis'],2)}"},
        ])
        st.caption(f"Descriptive statistics summarise the {F.intc(d['n'])} non-missing filtered "
                   "observations for the selected variable. They are not model-performance measures.")

        st.write("")
        L.section("Descriptive statistics across selected variables")
        chosen = st.multiselect("Variables", num_vars,
                                default=num_vars[: min(8, len(num_vars))], key="sa_desc_vars")
        if chosen:
            tbl = S.describe_table(sub, chosen)
            st.dataframe(tbl.round(4), use_container_width=True, hide_index=True)
            st.download_button("Download descriptive statistics (CSV)",
                               tbl.to_csv(index=False).encode("utf-8"),
                               file_name="descriptive_statistics.csv")

    # ---------------- Distributions ----------------
    with tabs[1]:
        var = st.selectbox("Variable", num_vars, key="sa_dist_var")
        c1, c2, c3 = st.columns(3)
        bins = c1.slider("Histogram bins", 5, 100, 30, key="sa_bins")
        logy = c2.checkbox("Log y-axis (histogram)", value=False, key="sa_logy")
        show_out = c3.checkbox("Show box-plot outliers", value=False, key="sa_showout")
        series = pd.to_numeric(sub[var], errors="coerce")
        clean = series.replace([np.inf, -np.inf], np.nan).dropna()
        st.caption(f"n = {F.intc(len(clean))} · missing = {F.intc(int(series.isna().sum()))}")
        cc1, cc2 = st.columns(2)
        with cc1:
            C.show(C.histogram(clean, bins=bins, x_title=var, log_y=logy, height=320))
        with cc2:
            C.show(C.box(clean, x_title=var, show_points=show_out, height=320))
        st.caption("Box-plot outliers use the IQR rule and are statistical flags, not "
                   "automatically data errors. No values are removed.")

        group_var = st.selectbox("Grouping category (violin)", ["(none)"] + group_vars,
                                 key="sa_dist_group")
        if group_var != "(none)" and len(clean) >= 10:
            gdf = sub[[group_var, var]].copy()
            gdf[var] = pd.to_numeric(gdf[var], errors="coerce")
            gdf = gdf.replace([np.inf, -np.inf], np.nan).dropna()
            if gdf[group_var].nunique() > 1:
                C.show(C.violin_by_group(gdf, group_var, var, height=340))
                st.caption("Distribution by group; groups with very small n should be read "
                           "with caution.")

    # ---------------- Trends over time ----------------
    with tabs[2]:
        dcols = [c for c in ("month", "date") if c in sub.columns]
        if not dcols:
            L.unavailable("a date column in this dataset")
        else:
            tcol = dcols[0]
            var = st.selectbox("Variable", num_vars, key="sa_ts_var")
            c1, c2, c3 = st.columns(3)
            agg = c1.selectbox("Aggregation", ["mean", "median", "sum"], key="sa_ts_agg")
            window = c2.slider("Rolling window (months)", 1, 12, 3, key="sa_ts_win")
            tsdf = sub[[tcol, var]].copy()
            tsdf[var] = pd.to_numeric(tsdf[var], errors="coerce")
            tsdf = tsdf.replace([np.inf, -np.inf], np.nan).dropna()
            if tsdf.empty:
                st.info("No valid observations after removing missing dates/values.")
            else:
                monthly = tsdf.groupby(tcol)[var].agg(agg).sort_index()
                counts = tsdf.groupby(tcol).size()
                mdf = pd.DataFrame({"value": monthly, "count": counts}).reset_index()
                mdf["rolling"] = mdf["value"].rolling(window, min_periods=1).mean()
                st.caption(f"{len(mdf)} months with observations · not interpolated across gaps.")
                f = C.line(mdf, tcol, "value", y_title=var, height=320)
                f.add_scatter(x=mdf[tcol], y=mdf["rolling"], mode="lines",
                              line=dict(color="#C4921C", width=2, dash="dot"),
                              name=f"{window}m rolling")
                C.show(f)
                cc1, cc2 = st.columns(2)
                with cc1:
                    C.show(C.bar(mdf, tcol, "count", y_title="Observations", height=260))
                with cc2:
                    g = monthly.diff().dropna().reset_index(name="change")
                    C.show(C.bar(g, tcol, "change", y_title=f"Δ {var}", height=260))
                # seasonal
                cal = "cal_month_y" if "cal_month_y" in sub.columns else (
                    "cal_month_x" if "cal_month_x" in sub.columns else None)
                if cal:
                    seas = tsdf.assign(cal=sub.loc[tsdf.index, cal]).groupby("cal")[var].agg(agg).reset_index()
                    C.show(C.bar(seas, "cal", var, x_title="Calendar month", y_title=var,
                                 height=260, title="Seasonal (month-of-year) summary"))
                # trend test
                tr = S.spearman_trend(mdf["value"], mdf[tcol].astype("int64"))
                if tr.get("ok"):
                    st.caption(f"Trend test — Spearman rank vs time: ρ = {F.num(tr['statistic'],3)}, "
                               f"p = {F.num(tr['p_value'],4)} (n = {tr['n']}), stars {S.p_to_stars(tr['p_value'])}. "
                               "Null hypothesis: no monotonic trend. A p-value is not the probability "
                               "that the null is true.")
                st.download_button("Download time-series summary (CSV)",
                                   mdf.to_csv(index=False).encode("utf-8"),
                                   file_name="timeseries_summary.csv")

    # ---------------- Group comparisons ----------------
    with tabs[3]:
        if not group_vars:
            L.unavailable("categorical grouping variables in this dataset")
        else:
            c1, c2 = st.columns(2)
            gcol = c1.selectbox("Group by", group_vars, key="sa_grp")
            var = c2.selectbox("Variable", num_vars, key="sa_grp_var")
            min_n = st.slider("Minimum group size", 1, 100, 5, key="sa_grp_min")
            gs = S.group_summary(sub, gcol, var, min_n=min_n)
            if gs.empty:
                st.info("No groups meet the minimum sample size.")
            else:
                c1, c2 = st.columns(2)
                with c1:
                    C.show(C.bar(gs.sort_values("mean", ascending=False), gcol, "mean",
                                 x_title=gcol, y_title=f"Mean {var}", height=340,
                                 title="Mean by group"))
                with c2:
                    gdf = sub[[gcol, var]].copy()
                    gdf[var] = pd.to_numeric(gdf[var], errors="coerce")
                    gdf = gdf.replace([np.inf, -np.inf], np.nan).dropna()
                    keep = gs[gcol]
                    gdf = gdf[gdf[gcol].isin(keep)]
                    if not gdf.empty:
                        C.show(C.box_by_group(gdf, gcol, var, height=340))
                st.dataframe(gs.round(4), use_container_width=True, hide_index=True)
                st.caption(f"Groups with n < {min_n} are excluded (threshold visible). "
                           "Very unequal or tiny samples should be interpreted cautiously.")
                st.download_button("Download group summary (CSV)",
                                   gs.to_csv(index=False).encode("utf-8"),
                                   file_name=f"group_summary_{gcol}.csv")

    # ---------------- Correlations ----------------
    with tabs[4]:
        defaults = [c for c in ["ret_z_cur", "ret_lag1", "ret_roll3", "spi", "peer_median",
                                "peer_count", "rain_anom_z", "rain_anom_lag1", "y1", "y2"]
                    if c in num_vars]
        sel = st.multiselect("Numeric variables", num_vars,
                             default=defaults or num_vars[: min(6, len(num_vars))],
                             key="sa_corr_vars")
        method_label = st.radio("Method", ["Pearson (linear)", "Spearman (rank)"],
                                horizontal=True, key="sa_corr_m")
        method = "pearson" if method_label.startswith("Pearson") else "spearman"
        st.caption("Pearson measures linear association; Spearman measures monotonic "
                   "association. Correlation does not establish causation.")
        if len(sel) >= 2:
            corr, counts = S.correlation_matrix(sub, sel, method=method)
            if not corr.empty:
                c1, c2 = st.columns([1.3, 1])
                with c1:
                    C.show(C.corr_heatmap(corr, height=420))
                with c2:
                    pairs = S.correlation_pairs(sub, sel, method=method).head(15)
                    st.dataframe(pairs.round(3), use_container_width=True, hide_index=True)
                with st.expander("Pairwise observation counts"):
                    st.dataframe(counts, use_container_width=True)
                    st.caption("Cells show the number of complete pairs used for each "
                               "correlation (pairwise-complete).")
                st.download_button("Download correlation matrix (CSV)",
                                   corr.round(4).to_csv().encode("utf-8"),
                                   file_name="correlation_matrix.csv")
                st.download_button("Download correlation pairs (CSV)",
                                   S.correlation_pairs(sub, sel, method=method).round(4)
                                   .to_csv(index=False).encode("utf-8"),
                                   file_name="correlation_pairs.csv")
            # scatter
            sc1, sc2 = st.columns(2)
            xv = sc1.selectbox("X variable", sel, key="sa_sc_x")
            yv = sc2.selectbox("Y variable", sel, index=min(1, len(sel) - 1), key="sa_sc_y")
            trend = st.checkbox("Add descriptive trend line (OLS)", value=False, key="sa_sc_trend")
            sdf = sub[[xv, yv]].apply(pd.to_numeric, errors="coerce").replace(
                [np.inf, -np.inf], np.nan).dropna()
            if len(sdf) >= 3 and xv != yv:
                C.show(C.scatter(sdf, xv, yv, trend=trend, height=340))
                st.caption(f"n = {F.intc(len(sdf))} complete pairs. Trend line is descriptive only.")
        else:
            st.info("Select at least two numeric variables.")

    # ---------------- Missingness & quality ----------------
    with tabs[5]:
        mt = S.missing_table(sub)
        st.caption(f"Sample: {F.intc(len(sub))} rows. Missingness is reported, never imputed.")
        if not mt.empty:
            top = mt.head(20)
            C.show(C.bar(top, "missing_pct", "variable", horizontal=True,
                         x_title="Missing (%)", height=max(300, 18 * len(top))))
            st.dataframe(mt, use_container_width=True, hide_index=True)
            st.download_button("Download missingness table (CSV)",
                               mt.to_csv(index=False).encode("utf-8"),
                               file_name="missingness_table.csv")
        st.markdown("**Duplicate rows**")
        st.caption(f"Full duplicate rows: {F.intc(int(sub.duplicated().sum()))} · "
                   f"constant columns: {F.intc(int(sum(sub[c].nunique(dropna=True) <= 1 for c in sub.columns)))}")
        if "month" in sub.columns:
            by_m = sub.groupby(sub["month"].dt.to_period("M").astype(str)).apply(
                lambda d: d.isna().mean().mean())
            bm = by_m.reset_index(name="missing_share")
            C.show(C.line(bm, "month", "missing_share", y_title="Mean missing share",
                          height=260, title="Missingness by month"))

    # ---------------- Statistical tests ----------------
    with tabs[6]:
        st.caption("Inferential tests run only when sample sizes and structure permit. "
                   "Assumptions and caveats are shown with every result.")
        if not group_vars:
            L.unavailable("grouping variables for inferential tests")
        else:
            c1, c2 = st.columns(2)
            gcol = c1.selectbox("Grouping variable", group_vars, key="sa_test_g")
            var = c2.selectbox("Response variable", num_vars, key="sa_test_var")
            levels = sub[gcol].dropna().value_counts()
            levels = levels[levels >= 3].index.tolist()
            test_kind = "Two groups" if len(levels) == 2 else (
                "Multiple groups" if len(levels) > 2 else "Insufficient groups")
            st.caption(f"{len(levels)} eligible groups (n ≥ 3): {', '.join(map(str, levels[:8]))} "
                       f"{'…' if len(levels) > 8 else ''}")
            if test_kind == "Insufficient groups":
                st.info("Not enough groups with sufficient observations to run a test.")
            else:
                choice = st.radio("Choose a test", (
                    ["Welch t-test", "Mann–Whitney U"] if test_kind == "Two groups"
                    else ["One-way ANOVA", "Kruskal–Wallis"]), key="sa_test_choice")
                groups = [pd.to_numeric(sub.loc[sub[gcol] == g, var], errors="coerce").dropna()
                          for g in levels]
                if test_kind == "Two groups":
                    res = (S.welch_ttest(groups[0], groups[1]) if choice.startswith("Welch")
                           else S.mannwhitney(groups[0], groups[1]))
                else:
                    res = (S.anova(groups) if choice.startswith("One-way")
                           else S.kruskal(groups))
                st.markdown(f"**Research question:** does *{var}* differ across *{gcol}*?")
                st.markdown("**Null hypothesis:** the distributions/means do not differ "
                            "across groups.")
                if res.get("ok"):
                    rows = [{"Statistic": res["test"], "Value": F.num(res["statistic"], 4),
                             "p-value": F.num(res["p_value"], 5),
                             "Stars": S.p_to_stars(res["p_value"])}]
                    if "n_a" in res:
                        rows.append({"Statistic": "n (group A / group B)",
                                     "Value": f"{res['n_a']} / {res['n_b']}", "p-value": "—", "Stars": ""})
                    if res.get("effect_size") is not None:
                        rows.append({"Statistic": "Cohen's d (effect size)",
                                     "Value": F.num(res["effect_size"], 3), "p-value": "—", "Stars": ""})
                    if res.get("ci"):
                        rows.append({"Statistic": "95% CI mean difference",
                                     "Value": f"[{F.num(res['ci'][0],3)}, {F.num(res['ci'][1],3)}]",
                                     "p-value": "—", "Stars": ""})
                    if "n_total" in res:
                        rows.append({"Statistic": "Total n / groups",
                                     "Value": f"{res['n_total']} / {res['n_groups']}",
                                     "p-value": "—", "Stars": ""})
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
                    st.caption("Assumptions: independent observations; Welch/ANOVA assume "
                               "approximate normality and unequal variance where applicable. "
                               "Mann–Whitney/Kruskal–Wallis are rank-based alternatives. "
                               "Multiple tests increase the chance of a false positive. "
                               "Significance is not practical importance.")
                else:
                    st.warning(f"Test not performed: {res.get('reason')}")
                if len(levels) > 2:
                    st.info("With many groups, consider a post-hoc correction for multiple "
                            "comparisons before drawing conclusions.")

    st.write("")
    L.section("Interpretation and limitations")
    st.markdown(
        "- Statistics describe the filtered observations only; they are not validation of the "
        "predictive models.\n"
        "- Correlations involving targets may reflect target construction or persistence.\n"
        "- Missing periods are shown via observation counts; series are not interpolated by default.\n"
        "- No values are deleted, imputed or winsorised as a side effect of visualisation.")
    st.caption(f"Note: {L.DISCLAIMER}")
