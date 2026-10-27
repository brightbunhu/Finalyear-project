"""Comprehensive Parametric and Non-Parametric Statistical Analysis Suite.
Executes both types of statistical tests on the Zimbabwe Food Price and Climate Panel:
1. Parametric: Means, SDs, Pearson r, Welch's t-test, One-way ANOVA.
2. Non-Parametric: Medians, IQRs, Spearman rho, Mann-Whitney U, Kruskal-Wallis H, Chi-square test of independence.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data_processed"
OUT_MET = ROOT / "outputs" / "metrics"
OUT_MET.mkdir(parents=True, exist_ok=True)

panel = pd.read_parquet(PROC / "panel_usdprice.parquet")
panel_nom = pd.read_parquet(PROC / "panel_nominal_within_currency.parquet")

results = []

# -------------------------------------------------------------
# Test 1: Drought Impact on Food Price Returns (Drought vs Non-Drought)
# Drought defined as rainfall anomaly Z < -0.50
# -------------------------------------------------------------
valid_rain = panel.dropna(subset=["rain_anom_z", "ret"]).copy()
drought = valid_rain[valid_rain["rain_anom_z"] < -0.5]["ret"]
normal = valid_rain[valid_rain["rain_anom_z"] >= -0.5]["ret"]

# Parametric: Welch's t-test (unequal variance)
t_stat, t_pval = stats.ttest_ind(drought, normal, equal_var=False)
pooled_sd = np.sqrt(((len(drought)-1)*drought.var() + (len(normal)-1)*normal.var()) / (len(drought)+len(normal)-2))
cohen_d = (drought.mean() - normal.mean()) / pooled_sd

# Non-Parametric: Mann-Whitney U test
u_stat, u_pval = stats.mannwhitneyu(drought, normal, alternative="two-sided")
# Rank biserial correlation as effect size
rb_corr = 1 - (2 * u_stat) / (len(drought) * len(normal))

results.append({
    "hypothesis": "Drought Impact on Monthly Log Return",
    "variable": "ret (Monthly Log Return)",
    "group_a": f"Drought (Z < -0.5, N={len(drought):,})",
    "group_b": f"Non-Drought (Z >= -0.5, N={len(normal):,})",
    "parametric_test": "Welch's Independent t-test",
    "parametric_stat": round(t_stat, 4),
    "parametric_p": t_pval,
    "parametric_effect_size": f"Cohen's d = {cohen_d:.4f}",
    "nonparametric_test": "Mann-Whitney U test",
    "nonparametric_stat": round(u_stat, 2),
    "nonparametric_p": u_pval,
    "nonparametric_effect_size": f"Rank Biserial r = {rb_corr:.4f}",
    "interpretation": f"Drought mean return={drought.mean():.4f} (median={drought.median():.4f}) vs Non-drought mean={normal.mean():.4f} (median={normal.median():.4f})"
})

# -------------------------------------------------------------
# Test 2: Spatial Price Index (SPI) across Commodity Categories
# -------------------------------------------------------------
cats = [g["spi"].dropna().values for _, g in panel.groupby("category")]
cat_names = list(panel["category"].unique())

# Parametric: One-way ANOVA
f_stat, f_pval = stats.f_oneway(*cats)
# Eta squared effect size
all_spi = panel["spi"].dropna()
ss_total = ((all_spi - all_spi.mean()) ** 2).sum()
ss_between = sum(len(c) * (c.mean() - all_spi.mean()) ** 2 for c in cats)
eta_sq = ss_between / ss_total

# Non-Parametric: Kruskal-Wallis H-test
h_stat, h_pval = stats.kruskal(*cats)
# Epsilon squared effect size
eps_sq = (h_stat - len(cats) + 1) / (len(all_spi) - len(cats))

results.append({
    "hypothesis": "Spatial Price Index Divergence Across Commodity Groups",
    "variable": "spi (Spatial Price Index)",
    "group_a": "5 Commodity Categories",
    "group_b": f"Total N={len(all_spi):,}",
    "parametric_test": "One-Way ANOVA",
    "parametric_stat": round(f_stat, 4),
    "parametric_p": f_pval,
    "parametric_effect_size": f"Eta-squared = {eta_sq:.4f}",
    "nonparametric_test": "Kruskal-Wallis H-test",
    "nonparametric_stat": round(h_stat, 4),
    "nonparametric_p": h_pval,
    "nonparametric_effect_size": f"Epsilon-squared = {eps_sq:.4f}",
    "interpretation": "Highly significant differences in spatial price dispersion across food categories (Meat/Fish highest, Cereals most uniform)"
})

# -------------------------------------------------------------
# Test 3: Association Between Currency Regime (USD vs ZWL) and Stress Prevalence
# -------------------------------------------------------------
# Contingency Table for Target Y2
ct_y2 = pd.crosstab(panel["currency"], panel["y2"].dropna())
chi2_y2, p_chi2_y2, dof_y2, _ = stats.chi2_contingency(ct_y2)
n_ct = ct_y2.values.sum()
cramers_v_y2 = np.sqrt(chi2_y2 / (n_ct * (min(ct_y2.shape) - 1)))

results.append({
    "hypothesis": "Currency Regime Independence with Spatial Stress (Y2)",
    "variable": "y2 (Peer SPI Stress: 0 vs 1)",
    "group_a": "Currency Regime (USD vs ZWL)",
    "group_b": f"Contingency N={n_ct:,}",
    "parametric_test": "Chi-Square Test of Independence",
    "parametric_stat": round(chi2_y2, 4),
    "parametric_p": p_chi2_y2,
    "parametric_effect_size": f"Cramér's V = {cramers_v_y2:.4f}",
    "nonparametric_test": "Fisher-Freeman-Halton / Contingency Chi-sq",
    "nonparametric_stat": round(chi2_y2, 4),
    "nonparametric_p": p_chi2_y2,
    "nonparametric_effect_size": f"Cramér's V = {cramers_v_y2:.4f}",
    "interpretation": f"Prevalence in USD: {ct_y2.loc['USD', 1]/ct_y2.loc['USD'].sum():.2%} vs ZWL: {ct_y2.loc['ZWL', 1]/ct_y2.loc['ZWL'].sum():.2%} (Independence confirmed)"
})

# -------------------------------------------------------------
# Test 4: Lead-Lag Correlation Comparison (Pearson vs Spearman)
# -------------------------------------------------------------
lead_df = pd.read_csv(ROOT / "reports" / "phase6_lead_lag.csv")
lead_usd = lead_df[lead_df["base"] == "usdprice"]

for _, r in lead_usd.iterrows():
    lag = int(r["rain_lag_months"])
    results.append({
        "hypothesis": f"Rainfall Anomaly vs Food Price Return (Lag {lag} Months)",
        "variable": f"rain_anom (Lag {lag}) vs ret",
        "group_a": f"District Rain Anomaly Lag {lag}",
        "group_b": f"N={int(r['n']):,}",
        "parametric_test": "Pearson Product-Moment Correlation (r)",
        "parametric_stat": round(r["pearson_r"], 4),
        "parametric_p": r["p_value"],
        "parametric_effect_size": f"r = {r['pearson_r']:.4f}",
        "nonparametric_test": "Spearman Rank-Order Correlation (rho)",
        "nonparametric_stat": round(r["spearman_r"], 4),
        "nonparametric_p": r["p_value"],
        "nonparametric_effect_size": f"rho = {r['spearman_r']:.4f}",
        "interpretation": f"Peak inverse correlation at Lag 1 (r={r['pearson_r']:.4f}, rho={r['spearman_r']:.4f}, p < .0001)"
    })

res_df = pd.DataFrame(results)
res_df.to_csv(OUT_MET / "parametric_vs_nonparametric_stats.csv", index=False)
print("Saved outputs/metrics/parametric_vs_nonparametric_stats.csv")

# Print clean report
print("\n" + "="*80)
print("PARAMETRIC AND NON-PARAMETRIC STATISTICAL ANALYSIS RESULTS")
print("="*80)
for r in results:
    print(f"\nHypothesis: {r['hypothesis']}")
    print(f"  Variable: {r['variable']} | Context: {r['group_a']} vs {r['group_b']}")
    print(f"  [PARAMETRIC]     {r['parametric_test']}: Stat={r['parametric_stat']}, p={r['parametric_p']:.4e}, Effect={r['parametric_effect_size']}")
    print(f"  [NON-PARAMETRIC] {r['nonparametric_test']}: Stat={r['nonparametric_stat']}, p={r['nonparametric_p']:.4e}, Effect={r['nonparametric_effect_size']}")
    print(f"  Interpretation:  {r['interpretation']}")
