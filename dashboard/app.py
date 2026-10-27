"""Zimbabwe Food-Price Stress - research dashboard (router).

Run:  streamlit run dashboard/app.py

Everything shown is read from artefacts produced by the pipeline
(data_processed/, artifacts/, models/, figures/, reports/). This is a RESEARCH
prototype. It is NOT an operational early-warning system. No value is
fabricated: where a figure cannot be derived from a real project artefact the
UI shows an explicit "not available" state.

The app is organised into 7 top-level sections (matching the reference design);
sub-pages inside a section are switched with a segmented control so only the
active sub-page is rendered.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional, Tuple

import streamlit as st

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import importlib
from components import layout as L  # noqa: E402
importlib.reload(L)
from components import charts as C  # noqa: E402
importlib.reload(C)
from utils import loaders as D  # noqa: E402

st.set_page_config(
    page_title="Zimbabwe Food-Price Stress | Early Warning Dashboard",
    page_icon="🇿🇼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# section label -> icon, subtitle, [(module or None, tab title), ...]
SECTIONS: List[Tuple[str, str, str, List[Tuple[Optional[str], str]]]] = [
    ("Home", "🏠",
     "Overview of food-price stress, data and model predictions for Zimbabwe.",
     [("pages.home", "Home")]),
    ("Make a Prediction", "✏️",
     "Score Y1/Y2 stress from stored features or your own inputs.",
     [("pages.prediction_studio", "Make a Prediction")]),
    ("Geographic Explorer", "🗺",
     "Spatial patterns and district-level model scores.",
     [("pages.geographic_explorer", "Geographic Explorer")]),
    ("Data & Integration", "▤",
     "Datasets, integration pipeline, coverage and data quality.",
     [("pages.data_integration", "Dataset Catalogue"),
      ("pages.coverage_quality", "Coverage & Quality"),
      ("pages.price_trends", "Price Trends"),
      ("pages.rainfall_climate", "Rainfall & Climate")]),
    ("Model Performance", "📈",
     "Compare models, evaluate predictive quality, and inspect validation results.",
     [("pages.model_performance", "Overview"),
      ("pages.historical_holdout", "Holdout Predictions"),
      ("pages.statistical_analysis", "Statistical Analysis")]),
    ("Reports & Downloads", "📄",
     "Research reports, figures, models and artefact downloads.",
     [("pages.reports_downloads", "Download Centre"),
      ("pages.research_evidence", "Research Evidence")]),
    ("About & Help", "ⓘ",
     "Project scope, methodology, glossary and limitations.",
     [("pages.about_help", "About & Help")]),
]

LABELS = [s[0] for s in SECTIONS]
ICONS = {s[0]: s[1] for s in SECTIONS}
SUBTITLES = {s[0]: s[2] for s in SECTIONS}
TABS = {s[0]: s[3] for s in SECTIONS}

# legacy ?page= values from the earlier 12-page layout -> section
_LEGACY = {
    "Home": "Home", "Prediction Studio": "Make a Prediction",
    "Make a Prediction": "Make a Prediction",
    "Geographic Explorer": "Geographic Explorer",
    "Data & Integration": "Data & Integration", "Coverage & Quality": "Data & Integration",
    "Price Trends": "Data & Integration", "Rainfall & Climate": "Data & Integration",
    "Model Performance": "Model Performance",
    "Historical Holdout Predictions": "Model Performance",
    "Historical Holdout": "Model Performance",
    "Statistical Analysis": "Model Performance",
    "Research Evidence": "Reports & Downloads",
    "Limitations & Interpretation": "About & Help", "Limitations": "About & Help",
}


def _resolve(qp: Optional[str]) -> str:
    if not qp:
        return LABELS[0]
    if qp in LABELS:
        return qp
    return _LEGACY.get(qp, LABELS[0])


def _meta() -> List[Tuple[str, str]]:
    """Real, artefact-derived header meta (no fabrication)."""
    try:
        panel = D.load_panel("usdprice")
        if panel is None or panel.empty or "month" not in panel.columns:
            return [("Latest data", "Not available"), ("Panel cells", "Not available")]
        latest = panel["month"].max()
        latest_s = f"{latest:%Y-%m}" if hasattr(latest, "year") else str(latest)
        n_mkts = panel["market_id"].nunique() if "market_id" in panel.columns else 0
        return [("Latest data", latest_s), ("Panel cells", f"{len(panel):,}"), ("Markets", f"{n_mkts:,}")]
    except Exception:
        return [("Latest data", "Not available"), ("Panel cells", "Not available")]


def _render_module(path: str) -> None:
    C.reset_cards()
    try:
        import importlib
        mod = __import__(path, fromlist=["render"])
        mod = importlib.reload(mod)
    except Exception as exc:
        st.error(f"This sub-page could not be loaded: {exc}")
        return
    render = getattr(mod, "render", None)
    if render is None:
        st.error(f"Page module {path} has no render() function.")
        return
    _ = render()


def _render_downloads() -> None:
    L.section("Artefact downloads",
              "Files produced by the pipeline; served directly from disk.")
    for sub in ("artifacts", "reports", "figures", "models"):
        d = ROOT / sub
        if not d.is_dir():
            continue
        files = sorted(p for p in d.iterdir() if p.is_file())
        if not files:
            continue
        L.section(f"{sub}/")
        for p in files:
            size = p.stat().st_size
            if size > 40_000_000:
                L.card(f'<div class="metric-lbl">{p.name}</div>'
                       f'<div class="metric-cap">{size/1e6:.1f} MB (too large to '
                       f'inline-download)</div>')
                continue
            try:
                data = p.read_bytes()
            except Exception:
                continue
            left, right = st.columns([4, 1])
            left.caption(f"{p.name}  ·  {size/1e3:.0f} KB")
            right.download_button("Download", data=data, file_name=p.name,
                                  key=f"dl_{sub}_{p.name}")


def _render_about() -> None:
    L.section("Project overview")
    st.markdown(
        '<div style="width:42px;height:28px;float:left;margin:0 14px 8px 0;border-radius:2px;'
        'background:linear-gradient(#2e9e4f 0 20%,#f2c230 0 35%,#d7261e 0 50%,#000 0 65%,'
        '#d7261e 0 80%,#f2c230 0 90%,#2e9e4f 0)"></div>'
        '<p style="font-size:12px;color:var(--mute);line-height:1.5">'
        'This dashboard presents the results of a research project predicting '
        'food-price stress in Zimbabwe using machine learning, integrating food-price, '
        'market, rainfall, geographic and contextual data. Every figure is read from '
        'the project artefacts produced by the pipeline.</p>',
        unsafe_allow_html=True)
    st.markdown(
        '<ul style="list-style:none;margin-top:6px;color:var(--mute);font-size:12px;'
        'clear:both"><li>◎ Research prototype</li>'
        '<li>◎ Not an operational early-warning system</li>'
        '<li>◎ For academic and research use only</li></ul>',
        unsafe_allow_html=True)
    L.section("Scope statement")
    L.note(L.DISCLAIMER)


def _render_static(title: str) -> None:
    if title == "Downloads":
        _render_downloads()
    else:
        _render_about()


def main() -> None:
    L.inject_css()

    if "nav_target" in st.session_state:
        st.session_state.nav = st.session_state.pop("nav_target")
    elif "nav" not in st.session_state:
        st.session_state.nav = _resolve(st.query_params.get("page"))

    L.sidebar_brand()
    chosen = st.sidebar.radio("Navigation", LABELS, key="nav", label_visibility="collapsed")
    L.sidebar_disclaimer()

    tabs = TABS[chosen]
    icon = ICONS[chosen]

    if chosen == "Home":
        meta = _meta()
        meta_html = ""
        if meta:
            cells = "".join(f'<span class="app-meta-item">{L.esc(k)}<b>{L.esc(v)}</b></span>' for k, v in meta)
            meta_html = f'<div class="app-meta">{cells}</div>'
        st.markdown(
            '<header class="appbar"><div class="appbar-id"><div class="flag" aria-hidden="true"></div>'
            '<div class="appbar-name"><strong>Zimbabwe Food-Price Stress</strong>'
            '<span>Early Warning ML System</span></div></div>'
            f'{meta_html}</header>',
            unsafe_allow_html=True
        )
        L.enable_page_header(True)
    else:
        L.enable_page_header(False)
        L.top(chosen, SUBTITLES[chosen], icon, meta=_meta())

    if len(tabs) == 1:
        path, _t = tabs[0]
        _ = _render_module(path) if path else _render_static(_t)
        return

    names = [t[1] for t in tabs]
    sel = st.segmented_control("Section", names, default=names[0],
                               key=f"sub__{chosen}", width="stretch",
                               label_visibility="collapsed")
    if sel not in names:
        sel = names[0]
    path, _t = next((t for t in tabs if t[1] == sel), tabs[0])
    _ = _render_module(path) if path else _render_static(_t)


if __name__ == "__main__":
    _ = main()
