"""Reusable Plotly figure builders. Functions return figures (they do not render)."""
from __future__ import annotations

from typing import List, Optional

import numpy as np
import pandas as pd

try:
    import plotly.graph_objects as go
    import plotly.express as px
except Exception:  # pragma: no cover
    go = None
    px = None

from components.layout import THEME

_BLUE = THEME["primary_blue"]
_TEAL = THEME["teal"]
_GREEN = THEME["green"]
_AMBER = THEME["amber"]
_CORAL = THEME["coral_red"]
_PURPLE = THEME["purple"]

_FONT = "Inter, Segoe UI, sans-serif"
_COLORWAY = [THEME["primary_blue"], THEME["teal"], THEME["amber"],
             THEME["coral_red"], THEME["purple"], THEME["green"], THEME["navy_sidebar"]]
_AXIS = dict(
    gridcolor=THEME["muted_bg"], zeroline=False, linecolor=THEME["border"],
    tickfont=dict(size=11, color=THEME["secondary_text"], family=_FONT),
)
_MISSING = "Not recorded"


def _axis_title(fig, axis: str, text: str) -> None:
    """Set an axis title only when there is real text.

    Plotly draws the word "undefined" when a title font is set and the
    title text is missing, so empty titles are left blank.
    """
    label = (text or "").strip()
    if not label or label.lower() == "undefined":
        return
    font = dict(size=12, color=THEME["mute"], family=_FONT)
    updater = fig.update_xaxes if axis == "x" else fig.update_yaxes
    updater(title=dict(text=label, font=font))


def _labels(series: pd.Series) -> pd.Series:
    """Category labels for legends and axes. Missing values stay visible."""
    out = series.astype("string")
    out = out.fillna(_MISSING)
    return out.replace({
        "": _MISSING, "nan": _MISSING, "None": _MISSING, "<NA>": _MISSING,
        "NaT": _MISSING, "undefined": _MISSING, "Undefined": _MISSING,
    })


def _clean(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    out = df.copy()
    for col in cols:
        if col not in out.columns:
            continue
        if pd.api.types.is_datetime64_any_dtype(out[col]) or pd.api.types.is_numeric_dtype(out[col]):
            continue
        out[col] = _labels(out[col])
    return out


def _blank(text) -> bool:
    label = "" if text is None else str(text).strip()
    return not label or label.lower() == "undefined"


def _clear_blank_titles(fig) -> None:
    """Drop title objects that have no text.

    Streamlit wraps ``layout.title.text`` in bold. A missing text becomes the
    word "undefined", and Plotly does the same for an axis title font with no
    text. Real titles are left in place.
    """
    if _blank(getattr(fig.layout.title, "text", None)):
        fig.layout.pop("title", None)
    for name in list(fig.layout):
        if not (name.startswith("xaxis") or name.startswith("yaxis")):
            continue
        axis = fig.layout[name]
        if axis is None:
            continue
        if _blank(getattr(axis.title, "text", None)):
            axis.pop("title", None)
    legend = fig.layout.legend
    if legend is not None and _blank(getattr(legend.title, "text", None)):
        legend.pop("title", None)


def _base_layout(fig, height: int = 320, title: str = "") -> None:
    title_text = (title or "").strip()
    has_title = bool(title_text) and title_text.lower() != "undefined"
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=36 if has_title else 8, b=8),
        plot_bgcolor="white", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family=_FONT, size=12, color=THEME["ink"]),
        colorway=_COLORWAY,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                    font=dict(size=11, color=THEME["mute"], family=_FONT),
                    bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(font_size=12, font_family=_FONT),
    )
    if has_title:
        fig.update_layout(
            title=dict(text=title_text, font=dict(size=14, color=THEME["ink"], family=_FONT)))
    fig.update_xaxes(**_AXIS)
    fig.update_yaxes(**_AXIS)
    _clear_blank_titles(fig)


def line(df: pd.DataFrame, x: str, y: str, title: str = "", color: str = _BLUE,
         y_title: str = "", height: int = 320) -> "go.Figure":
    fig = go.Figure(go.Scatter(
        x=df[x], y=df[y], mode="lines+markers", name=y_title or y,
        line=dict(color=color, width=2), marker=dict(size=4),
        hovertemplate="%{x}<br>%{y}<extra></extra>"))
    _base_layout(fig, height, title)
    _axis_title(fig, "y", y_title)
    return fig


def multi_line(df: pd.DataFrame, x: str, y: str, color_col: str, title: str = "",
               y_title: str = "", height: int = 340) -> "go.Figure":
    plot_df = _clean(df, [color_col])
    fig = px.line(plot_df, x=x, y=y, color=color_col, markers=True,
                  color_discrete_sequence=_COLORWAY)
    _base_layout(fig, height, title)
    _axis_title(fig, "y", y_title)
    return fig


def bar(df: pd.DataFrame, x: str, y: str, title: str = "", horizontal: bool = False,
        color: str = _BLUE, x_title: str = "", y_title: str = "",
        height: int = 320) -> "go.Figure":
    plot_df = _clean(df, [x, y])
    if horizontal:
        fig = go.Figure(go.Bar(x=plot_df[x], y=plot_df[y], orientation="h", marker_color=color))
        fig.update_yaxes(autorange="reversed")
    else:
        fig = go.Figure(go.Bar(x=plot_df[x], y=plot_df[y], marker_color=color))
    _base_layout(fig, height, title)
    _axis_title(fig, "x", x_title)
    _axis_title(fig, "y", y_title)
    if horizontal:
        fig.update_yaxes(autorange="reversed")
    return fig


def histogram(series: pd.Series, bins: int = 30, title: str = "", x_title: str = "",
              log_y: bool = False, height: int = 320) -> "go.Figure":
    fig = go.Figure(go.Histogram(x=series, nbinsx=int(bins), marker_color=_BLUE, name="Count"))
    _base_layout(fig, height, title)
    _axis_title(fig, "x", x_title)
    fig.update_yaxes(type="log" if log_y else "linear")
    _axis_title(fig, "y", "Count")
    return fig


def box(series: pd.Series, title: str = "", x_title: str = "", show_points: bool = False,
        height: int = 320) -> "go.Figure":
    fig = go.Figure(go.Box(y=series, boxpoints="outliers" if show_points else False,
                           marker_color=_TEAL, line_color=_TEAL, name=x_title or "Value"))
    _base_layout(fig, height, title)
    _axis_title(fig, "y", x_title)
    return fig


def box_by_group(df: pd.DataFrame, group_col: str, value_col: str, title: str = "",
                 height: int = 340) -> "go.Figure":
    fig = px.box(_clean(df, [group_col]), x=group_col, y=value_col, color=group_col,
                 color_discrete_sequence=_COLORWAY)
    _base_layout(fig, height, title)
    fig.update_layout(showlegend=False)
    return fig


def violin_by_group(df: pd.DataFrame, group_col: str, value_col: str, title: str = "",
                    height: int = 340) -> "go.Figure":
    fig = px.violin(_clean(df, [group_col]), x=group_col, y=value_col, color=group_col,
                    box=True, points=False, color_discrete_sequence=_COLORWAY)
    _base_layout(fig, height, title)
    fig.update_layout(showlegend=False)
    return fig


def corr_heatmap(corr: pd.DataFrame, title: str = "", height: int = 420) -> "go.Figure":
    fig = go.Figure(go.Heatmap(
        z=corr.values, x=list(corr.columns), y=list(corr.index),
        colorscale="RdBu", zmid=0, zmin=-1, zmax=1,
        colorbar=dict(thickness=12)))
    _base_layout(fig, height, title)
    return fig


def scatter(df: pd.DataFrame, x: str, y: str, title: str = "", trend: bool = False,
            color_col: Optional[str] = None, height: int = 340) -> "go.Figure":
    plot_df = _clean(df, [color_col] if color_col else [])
    fig = px.scatter(plot_df, x=x, y=y, color=color_col, trendline="ols" if trend else None,
                     opacity=0.6, color_discrete_sequence=_COLORWAY)
    _base_layout(fig, height, title)
    return fig


def choropleth(df: pd.DataFrame, geo: dict, loc: str, val: str, title: str = "",
               colorscale: str = "YlOrRd", vmin: float = 0.0, vmax: float = 1.0,
               height: int = 420, colorbar_title: str = "Value") -> "go.Figure":
    """Choropleth map with OpenStreetMap tiles displaying Zimbabwe districts."""
    plot_df = df.copy()
    if loc in plot_df.columns:
        plot_df[loc] = plot_df[loc].astype(str)

    if hasattr(px, "choropleth_map"):
        fig = px.choropleth_map(
            plot_df, geojson=geo, locations=loc,
            featureidkey="properties.shapeName", color=val,
            map_style="open-street-map",
            center=dict(lat=-19.0154, lon=29.1549), zoom=5.4,
            opacity=0.68,
            color_continuous_scale=colorscale, range_color=(vmin, vmax),
            labels={val: colorbar_title or "Value", loc: "District"}
        )
    else:
        fig = px.choropleth_mapbox(
            plot_df, geojson=geo, locations=loc,
            featureidkey="properties.shapeName", color=val,
            mapbox_style="open-street-map",
            center=dict(lat=-19.0154, lon=29.1549), zoom=5.4,
            opacity=0.68,
            color_continuous_scale=colorscale, range_color=(vmin, vmax),
            labels={val: colorbar_title or "Value", loc: "District"}
        )

    fig.update_layout(
        height=height, margin=dict(l=0, r=0, t=28 if title else 4, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family=_FONT, size=12, color=THEME["ink"]),
        coloraxis_colorbar=dict(
            title=dict(text=colorbar_title or "Value",
                       font=dict(size=11, color=THEME["mute"])),
            thickness=14, len=0.8,
            tickfont=dict(size=11, color=THEME["mute"]),
        ),
    )
    if title:
        fig.update_layout(title=dict(text=title, font=dict(size=14, color=THEME["ink"], family=_FONT)))
    _clear_blank_titles(fig)
    return fig


def confusion(cm: np.ndarray, labels: List[str], title: str = "",
              height: int = 320) -> "go.Figure":
    fig = go.Figure(go.Heatmap(z=cm, x=labels, y=labels, colorscale="Blues",
                               text=cm, texttemplate="%{text}", showscale=False))
    _base_layout(fig, height, title)
    _axis_title(fig, "y", "Actual")
    _axis_title(fig, "x", "Predicted")
    fig.update_yaxes(autorange="reversed")
    return fig


def generate_static_map_png(df: pd.DataFrame, geo_path: Optional[Path] = None, title: str = "Zimbabwe Food-Price Stress — District Risk Distribution") -> bytes:
    """Generate a publication-grade static PNG map using GeoPandas and Matplotlib for offline inspection."""
    import io
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    import geopandas as gpd

    if geo_path is None or not Path(geo_path).exists():
        geo_path = Path(__file__).resolve().parents[2] / "data_processed" / "zwe_adm2_simplified.geojson"
        if not geo_path.exists():
            geo_path = Path(__file__).resolve().parents[2] / "raw" / "geo" / "zwe_adm2_geoboundaries.geojson"

    gdf = gpd.read_file(geo_path)
    merged = gdf.merge(df, left_on="shapeName", right_on="district", how="left")

    fig, ax = plt.subplots(figsize=(11, 9), dpi=200)
    fig.patch.set_facecolor("#F8FAFC")
    ax.set_facecolor("#F8FAFC")

    # Base neutral fill for all administrative districts
    merged.plot(ax=ax, color="#E2E8F0", edgecolor="#64748B", linewidth=0.6)

    colors = {
        "Very High Risk": "#EF4444",
        "High Risk": "#F97316",
        "Medium Risk": "#F59E0B",
        "Low Risk": "#10B981",
    }
    for rlabel, color in colors.items():
        subset = merged[merged["risk_label"] == rlabel]
        if not subset.empty:
            subset.plot(ax=ax, color=color, edgecolor="#1E293B", linewidth=0.8)

    ax.set_title(title, fontsize=14, fontweight="bold", color="#082B52", pad=16)
    ax.text(0.5, 1.01, "Zimbabwe Food-Price Stress ML Early Warning System · OpenStreetMap & geoBoundaries",
            transform=ax.transAxes, ha="center", fontsize=9, color="#64748B")

    legend_elements = [
        Patch(facecolor="#EF4444", edgecolor="#1E293B", label="Very High Risk"),
        Patch(facecolor="#F97316", edgecolor="#1E293B", label="High Risk"),
        Patch(facecolor="#F59E0B", edgecolor="#1E293B", label="Medium Risk"),
        Patch(facecolor="#10B981", edgecolor="#1E293B", label="Low Risk"),
        Patch(facecolor="#E2E8F0", edgecolor="#64748B", label="Unmonitored / Baseline"),
    ]
    ax.legend(handles=legend_elements, loc="lower left", frameon=True,
              facecolor="#FFFFFF", edgecolor="#CBD5E1", fontsize=9, title="Risk Category", title_fontsize=10)
    ax.axis("off")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


PLOTLY_CONFIG = {"displayModeBar": False, "responsive": True}


_CARD_SEQ = 0


def reset_cards() -> None:
    """Reset the per-run card counter (call once at the start of each render)."""
    global _CARD_SEQ
    _CARD_SEQ = 0


def show(fig, use_container_width: bool = True, title: str = "") -> None:
    """Render a figure inside the design's white card frame."""
    global _CARD_SEQ
    import streamlit as st
    _CARD_SEQ += 1
    with st.container(key=f"chartcard_{_CARD_SEQ}"):
        if title:
            st.markdown(f'<div class="card-title">{title}</div>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=use_container_width, config=PLOTLY_CONFIG)
