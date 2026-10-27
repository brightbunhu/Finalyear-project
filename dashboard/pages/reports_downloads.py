"""Reports & Downloads — comprehensive artefact download centre."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple
import streamlit as st

from components import layout as L
from utils import loaders as D

ROOT = Path(__file__).resolve().parents[2]


@st.cache_data(show_spinner=False)
def _read_file_bytes(path_str: str) -> bytes:
    """Cache file reading on demand so files are not re-read from disk on every rerun."""
    p = Path(path_str)
    if p.exists() and p.is_file():
        return p.read_bytes()
    return b""


def _get_file_info(p: Path, category: str) -> Dict[str, str]:
    ext = p.suffix.lower().lstrip(".")
    type_map = {
        "md": "Markdown Report",
        "csv": "CSV Dataset",
        "parquet": "Parquet Table",
        "json": "JSON Metadata",
        "joblib": "Scikit-Learn / ML Model",
        "png": "PNG Figure / Plot",
        "txt": "Log File",
    }
    file_type = type_map.get(ext, ext.upper() or "Binary File")
    size_bytes = p.stat().st_size
    if size_bytes >= 1_000_000:
        size_str = f"{size_bytes / 1e6:.2f} MB"
    else:
        size_str = f"{max(1, size_bytes // 1024)} KB"

    # Descriptions
    desc_map = {
        "phase10_qa_and_limitations.md": "Quality assurance report, edge-case audit, and validation boundary documentation",
        "phase2_target_definition.md": "Mathematical specification of prediction targets Y1 (surge) and Y2 (peer-relative stress)",
        "phase6b_diagnostics.md": "Statistical diagnostics, bootstrap validation, and threshold sensitivity analysis",
        "phase6b_bootstrap_ci.csv": "Bootstrapped 95% confidence intervals across all evaluated models",
        "phase6b_threshold_model_sensitivity.csv": "Threshold tuning curves and precision-recall trade-offs",
        "phase6b_window_recalibration.csv": "Rolling window recalibration evaluation",
        "metrics_all_tasks.csv": "Comprehensive cross-validation and forward-holdout evaluation metrics across all tasks",
        "optuna_summary.csv": "Hyperparameter optimization trial summaries and best parameter sets",
        "run_metadata.json": "Reproducibility metadata, software environment versions, and seed configuration",
        "y1_return_histgbm_usd.joblib": "Trained HistGradientBoosting pipeline for return surge prediction (USD)",
        "y1_return_histgbm_usd.meta.json": "Model card, input schema, hyperparameter choices, and training boundaries for Y1",
        "y2_peer_histgbm_usd.joblib": "Trained HistGradientBoosting pipeline for spatial price stress prediction (USD)",
        "y2_peer_histgbm_usd.meta.json": "Model card, input schema, hyperparameter choices, and training boundaries for Y2",
        "preds_T1_usd_y1.parquet": "Holdout prediction scores and test features for Task 1 (USD Y1)",
        "preds_T2_usd_y2.parquet": "Holdout prediction scores and test features for Task 2 (USD Y2)",
        "preds_T3_nominal_y1.parquet": "Holdout prediction scores and test features for Task 3 (Nominal Y1)",
        "preds_T4_nominal_y2.parquet": "Holdout prediction scores and test features for Task 4 (Nominal Y2)",
    }
    desc = desc_map.get(p.name, f"Pipeline output artefact from {category} directory")

    return {
        "path": str(p),
        "name": p.name,
        "type": file_type,
        "category": category,
        "size": size_str,
        "size_bytes": size_bytes,
        "desc": desc,
    }


def _render_file_table(file_list: List[Dict[str, str]], tab_prefix: str) -> None:
    if not file_list:
        st.info("No files available in this category.")
        return

    st.markdown(
        f'<div style="font-size:12.5px;color:var(--text-secondary);margin-bottom:12px;">'
        f'Showing {len(file_list)} files generated directly by the project pipeline. All downloads are served from disk.</div>',
        unsafe_allow_html=True
    )

    for i, item in enumerate(file_list):
        with st.container():
            c1, c2, c3, c4 = st.columns([2.5, 1.4, 3.2, 1.2], gap="small")
            with c1:
                st.markdown(f'<b style="font-size:13.5px;color:var(--navy);">{L.esc(item["name"])}</b>', unsafe_allow_html=True)
                st.caption(f"Size: {item['size']}")
            with c2:
                st.markdown(f'<span class="badge info">{item["type"]}</span>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div style="font-size:12.5px;color:var(--text-secondary);">{L.esc(item["desc"])}</div>', unsafe_allow_html=True)
            with c4:
                file_data = _read_file_bytes(item["path"])
                st.download_button(
                    "Download",
                    data=file_data,
                    file_name=item["name"],
                    key=f"dl_{tab_prefix}_{i}_{item['name']}",
                    use_container_width=True
                )
            st.markdown('<hr style="margin:8px 0;border:none;border-bottom:1px solid var(--border);">', unsafe_allow_html=True)


def render() -> None:
    L.page_header(
        "Reports & Downloads",
        "Download research reports, evaluation diagnostics, trained ML models, and dataset artefacts generated by the pipeline.",
        provenance="Read directly from reports/, figures/, models/, and artifacts/."
    )

    # Collect files
    categories = {
        "Reports": ROOT / "reports",
        "Figures": ROOT / "figures",
        "Models": ROOT / "models",
        "Data Files": ROOT / "artifacts",
    }

    categorized_files: Dict[str, List[Dict[str, str]]] = {}
    all_files: List[Dict[str, str]] = []

    for cat_name, cat_dir in categories.items():
        if cat_dir.is_dir():
            cat_list = []
            for p in sorted(cat_dir.iterdir()):
                if p.is_file() and p.stat().st_size <= 50_000_000:
                    info = _get_file_info(p, cat_name)
                    cat_list.append(info)
                    all_files.append(info)
            categorized_files[cat_name] = cat_list
        else:
            categorized_files[cat_name] = []

    # 5 Required Tabs
    tab_all, tab_rep, tab_fig, tab_mod, tab_dat = st.tabs([
        f"All Files ({len(all_files)})",
        f"Reports ({len(categorized_files.get('Reports', []))})",
        f"Figures ({len(categorized_files.get('Figures', []))})",
        f"Models ({len(categorized_files.get('Models', []))})",
        f"Data Files ({len(categorized_files.get('Data Files', []))})"
    ])

    with tab_all:
        L.section("All Pipeline Output Artefacts")
        _render_file_table(all_files, "all")

    with tab_rep:
        L.section("Research Reports & Diagnostic Documents")
        _render_file_table(categorized_files.get("Reports", []), "rep")

    with tab_fig:
        L.section("High-Resolution Empirical Figures & Curves")
        _render_file_table(categorized_files.get("Figures", []), "fig")

    with tab_mod:
        L.section("Trained Machine Learning Models & Metadata Cards")
        _render_file_table(categorized_files.get("Models", []), "mod")

    with tab_dat:
        L.section("Data Tables, Split Metrics & Predictions")
        _render_file_table(categorized_files.get("Data Files", []), "dat")
