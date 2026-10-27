"""Reusable statistical calculations for the Statistical Analysis page.

Pure functions (no Streamlit) so they can be unit-tested independently. All
functions guard against empty data, all-null columns, non-numeric input, small
samples and constant variables, and never mutate the input frame.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

try:
    from scipy import stats as _sps
except Exception:  # pragma: no cover
    _sps = None


_MIN_N = 3


def _clean_numeric(s: pd.Series) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce")
    x = x.replace([np.inf, -np.inf], np.nan).dropna()
    return x


def describe(series: pd.Series, percentiles: bool = True,
             skew_kurt: bool = True) -> Dict[str, Optional[float]]:
    """Descriptive statistics for one variable on the filtered observations."""
    raw = pd.to_numeric(series, errors="coerce")
    total = int(len(raw))
    x = _clean_numeric(series)
    n = int(len(x))
    out: Dict[str, Optional[float]] = {
        "n": n,
        "missing": total - n,
        "missing_pct": round(100 * (total - n) / total, 2) if total else None,
        "mean": None, "median": None, "std": None, "min": None, "max": None,
        "q1": None, "q3": None, "iqr": None, "skew": None, "kurtosis": None,
        "unique": int(x.nunique()),
    }
    if n == 0:
        return out
    out["mean"] = float(x.mean())
    out["median"] = float(x.median())
    out["std"] = float(x.std(ddof=1)) if n > 1 else None
    out["min"] = float(x.min())
    out["max"] = float(x.max())
    if percentiles:
        q1, q3 = np.percentile(x, [25, 75])
        out["q1"], out["q3"] = float(q1), float(q3)
        out["iqr"] = float(q3 - q1)
    if skew_kurt and n >= _MIN_N and x.nunique() > 1:
        out["skew"] = float(x.skew())
        out["kurtosis"] = float(x.kurtosis())
    return out


def describe_table(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    rows = []
    for c in cols:
        if c not in df.columns:
            continue
        d = describe(df[c])
        d = {"variable": c, **d}
        rows.append(d)
    if not rows:
        return pd.DataFrame(columns=["variable", "n", "missing", "missing_pct", "mean",
                                     "median", "std", "min", "q1", "q3", "max",
                                     "iqr", "skew", "kurtosis", "unique"])
    return pd.DataFrame(rows)


def missing_table(df: pd.DataFrame) -> pd.DataFrame:
    if df.shape[1] == 0:
        return pd.DataFrame(columns=["variable", "missing", "missing_pct", "dtype", "unique"])
    n = len(df)
    rows = []
    for c in df.columns:
        miss = int(df[c].isna().sum())
        rows.append({
            "variable": c,
            "missing": miss,
            "missing_pct": round(100 * miss / n, 2) if n else None,
            "dtype": str(df[c].dtype),
            "unique": int(df[c].nunique(dropna=True)),
            "constant": bool(df[c].nunique(dropna=True) <= 1),
        })
    return pd.DataFrame(rows).sort_values("missing_pct", ascending=False)


def outlier_flags(series: pd.Series, k: float = 1.5) -> pd.Series:
    """IQR-rule flags (named method, not proof of invalidity)."""
    x = pd.to_numeric(series, errors="coerce")
    q1, q3 = x.quantile(0.25), x.quantile(0.75)
    iqr = q3 - q1
    if iqr == 0 or np.isnan(iqr):
        return pd.Series(False, index=series.index)
    lo, hi = q1 - k * iqr, q3 + k * iqr
    return (x < lo) | (x > hi)


def correlation_matrix(df: pd.DataFrame, cols: List[str],
                       method: str = "pearson") -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Return (correlation matrix, pairwise n-count matrix) using pairwise-complete obs."""
    cols = [c for c in cols if c in df.columns]
    if len(cols) < 2:
        return pd.DataFrame(), pd.DataFrame()
    sub = df[cols].apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan)
    corr = sub.corr(method=method, min_periods=_MIN_N)
    m = sub.notna().astype(int)
    counts = m.T.dot(m).copy()
    arr = counts.to_numpy(copy=True)
    np.fill_diagonal(arr, sub.notna().sum().to_numpy())
    counts = pd.DataFrame(arr, index=counts.index, columns=counts.columns)
    return corr, counts


def correlation_pairs(df: pd.DataFrame, cols: List[str], method: str = "pearson") -> pd.DataFrame:
    cols = [c for c in cols if c in df.columns]
    rows = []
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            a, b = cols[i], cols[j]
            pair = df[[a, b]].apply(pd.to_numeric, errors="coerce").replace(
                [np.inf, -np.inf], np.nan).dropna()
            n = len(pair)
            r = np.nan
            if n >= _MIN_N and pair[a].nunique() > 1 and pair[b].nunique() > 1:
                r = float(pair[a].corr(pair[b], method=method))
            rows.append({"variable_a": a, "variable_b": b, "n": n,
                         "correlation": r})
    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.reindex(out["correlation"].abs().sort_values(ascending=False).index)
    return out


def group_summary(df: pd.DataFrame, group_col: str, value_col: str,
                  min_n: int = 1) -> pd.DataFrame:
    if group_col not in df.columns or value_col not in df.columns:
        return pd.DataFrame()
    sub = df[[group_col, value_col]].copy()
    sub[value_col] = pd.to_numeric(sub[value_col], errors="coerce")
    sub = sub.replace([np.inf, -np.inf], np.nan)
    g = sub.groupby(group_col)[value_col]
    out = pd.DataFrame({
        "n": g.count(),
        "missing": g.apply(lambda s: int(s.isna().sum())),
        "mean": g.mean(),
        "median": g.median(),
        "std": g.std(),
        "q1": g.quantile(0.25),
        "q3": g.quantile(0.75),
        "min": g.min(),
        "max": g.max(),
    }).reset_index()
    out = out[out["n"] >= min_n]
    return out.sort_values("mean", ascending=False, na_position="last")


# ------------------------------------------------------------- inferential
def welch_ttest(a: pd.Series, b: pd.Series) -> Dict:
    a, b = _clean_numeric(a), _clean_numeric(b)
    if _sps is None or len(a) < _MIN_N or len(b) < _MIN_N:
        return {"ok": False, "reason": "insufficient observations (need ≥ 3 per group)"}
    t, p = _sps.ttest_ind(a, b, equal_var=False)
    return {"ok": True, "test": "Welch t-test", "statistic": float(t), "p_value": float(p),
            "n_a": len(a), "n_b": len(b),
            "effect_size": _cohend(a, b),
            "ci": _mean_diff_ci(a, b)}


def mannwhitney(a: pd.Series, b: pd.Series) -> Dict:
    a, b = _clean_numeric(a), _clean_numeric(b)
    if _sps is None or len(a) < _MIN_N or len(b) < _MIN_N:
        return {"ok": False, "reason": "insufficient observations (need ≥ 3 per group)"}
    u, p = _sps.mannwhitneyu(a, b, alternative="two-sided")
    return {"ok": True, "test": "Mann–Whitney U", "statistic": float(u), "p_value": float(p),
            "n_a": len(a), "n_b": len(b)}


def anova(groups: List[np.ndarray]) -> Dict:
    groups = [_clean_numeric(pd.Series(g)) for g in groups]
    groups = [g for g in groups if len(g) >= 2]
    if _sps is None or len(groups) < 2:
        return {"ok": False, "reason": "need ≥ 2 groups with ≥ 2 observations"}
    f, p = _sps.f_oneway(*groups)
    return {"ok": True, "test": "One-way ANOVA", "statistic": float(f), "p_value": float(p),
            "n_groups": len(groups), "n_total": int(sum(len(g) for g in groups))}


def kruskal(groups: List[np.ndarray]) -> Dict:
    groups = [_clean_numeric(pd.Series(g)) for g in groups]
    groups = [g for g in groups if len(g) >= 2]
    if _sps is None or len(groups) < 2:
        return {"ok": False, "reason": "need ≥ 2 groups with ≥ 2 observations"}
    h, p = _sps.kruskal(*groups)
    return {"ok": True, "test": "Kruskal–Wallis H", "statistic": float(h), "p_value": float(p),
            "n_groups": len(groups), "n_total": int(sum(len(g) for g in groups))}


def chi_square(ct: pd.DataFrame) -> Dict:
    if _sps is None or ct.shape[0] < 2 or ct.shape[1] < 2:
        return {"ok": False, "reason": "need a ≥2×2 contingency table"}
    chi2, p, dof, expected = _sps.chi2_contingency(ct)
    return {"ok": True, "test": "Chi-square", "statistic": float(chi2), "p_value": float(p),
            "dof": int(dof), "min_expected": float(expected.min()),
            "n": int(ct.values.sum())}


def spearman_trend(series: pd.Series, x: Optional[pd.Series] = None) -> Dict:
    y = _clean_numeric(series)
    if _sps is None or len(y) < _MIN_N:
        return {"ok": False, "reason": "insufficient observations"}
    if x is None:
        x = pd.Series(np.arange(len(y)))
    x = pd.to_numeric(x, errors="coerce")
    pair = pd.DataFrame({"x": x, "y": y.values if hasattr(y, "values") else y}).dropna()
    if len(pair) < _MIN_N or pair["x"].nunique() < 2:
        return {"ok": False, "reason": "insufficient variation"}
    rho, p = _sps.spearmanr(pair["x"], pair["y"])
    return {"ok": True, "test": "Spearman rank trend", "statistic": float(rho),
            "p_value": float(p), "n": len(pair)}


def _cohend(a: pd.Series, b: pd.Series) -> Optional[float]:
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return None
    va, vb = a.var(ddof=1), b.var(ddof=1)
    pooled = np.sqrt(((na - 1) * va + (nb - 1) * vb) / (na + nb - 2))
    return float((a.mean() - b.mean()) / pooled) if pooled else None


def _mean_diff_ci(a: pd.Series, b: pd.Series, conf: float = 0.95) -> Optional[List[float]]:
    na, nb = len(a), len(b)
    if _sps is None or na < 2 or nb < 2:
        return None
    se = np.sqrt(a.var(ddof=1) / na + b.var(ddof=1) / nb)
    if se == 0:
        return None
    diff = float(a.mean() - b.mean())
    dof = (a.var(ddof=1) / na + b.var(ddof=1) / nb) ** 2 / (
        (a.var(ddof=1) / na) ** 2 / (na - 1) + (b.var(ddof=1) / nb) ** 2 / (nb - 1))
    t = _sps.t.ppf(1 - (1 - conf) / 2, dof)
    return [diff - t * se, diff + t * se]


def p_to_stars(p: float) -> str:
    if p is None or (isinstance(p, float) and np.isnan(p)):
        return ""
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return "ns"
