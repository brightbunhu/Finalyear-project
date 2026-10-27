"""Shared layout, theme tokens and small UI components.

Presentation only. Risk-band colours (r1–r5) keep their existing meanings.
Navigation icon order matches the section list in dashboard/app.py.
"""
from __future__ import annotations

import html
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple
from urllib.parse import quote

import streamlit as st

# Exact design tokens from prompt
THEME = {
    # Core palette
    "navy_sidebar": "#082B52",
    "navy_dark": "#061D38",
    "primary_blue": "#2563EB",
    "blue_hover": "#1D4ED8",
    "teal": "#0D9488",
    "green": "#10B981",
    "amber": "#F59E0B",
    "coral_red": "#EF4444",
    "purple": "#8B5CF6",
    "page_bg": "#F4F8FC",
    "card_bg": "#FFFFFF",
    "blue_surface": "#EAF3FF",
    "main_text": "#172B4D",
    "secondary_text": "#64748B",
    "border": "#DCE6F0",
    "muted_bg": "#EEF2F7",

    # Risk colours
    "risk_very_high": "#EF4444",
    "risk_high": "#F97316",
    "risk_medium": "#F59E0B",
    "risk_low": "#10B981",

    # Compatibility aliases
    "navy950": "#061D38", "navy900": "#082B52", "navy800": "#0B3D73",
    "blue700": "#2563EB", "blue600": "#1D4ED8", "blue100": "#EAF3FF",
    "teal600": "#0D9488", "green500": "#10B981", "green700": "#10B981",
    "amber500": "#F59E0B", "amber600": "#F59E0B", "amber700": "#F59E0B",
    "orange500": "#F97316", "red500": "#EF4444", "red700": "#EF4444",
    "purple600": "#8B5CF6", "purple700": "#8B5CF6",
    "slate950": "#172B4D", "slate700": "#475569", "slate500": "#64748B",
    "slate300": "#DCE6F0", "slate50": "#F4F8FC", "white": "#FFFFFF",
    "ink": "#172B4D", "mute": "#64748B", "line": "#DCE6F0", "bg": "#F4F8FC",
    "card": "#FFFFFF",
    "r1": "#EF4444", "r2": "#F97316", "r3": "#F59E0B", "r4": "#10B981", "r5": "#10B981",
    "ok": "#10B981",
}

DISCLAIMER = ("Research prototype. Predictions are model outputs from the stored "
              "research models. They are not prospectively validated official "
              "early-warning forecasts or official food-security classifications.")

# Lucide-style outlines. Key order matches SECTIONS in dashboard/app.py.
_NAV_ICONS = {
    "Home": (
        "<path d='M3 9.5L12 3l9 6.5V20a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1z'/>"
        "<polyline points='9 22 9 12 15 12 15 22'/>"
    ),
    "Make a Prediction": (
        "<path d='M12 20h9'/>"
        "<path d='M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z'/>"
    ),
    "Geographic Explorer": (
        "<circle cx='12' cy='10' r='3'/>"
        "<path d='M12 21.7C17.3 17 20 13 20 10a8 8 0 1 0-16 0c0 3 2.7 6.9 8 11.7z'/>"
    ),
    "Data & Integration": (
        "<ellipse cx='12' cy='5' rx='9' ry='3'/>"
        "<path d='M21 12c0 1.66-4 3-9 3s-9-1.34-9-3'/>"
        "<path d='M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5'/>"
    ),
    "Model Performance": (
        "<polyline points='22 12 18 12 15 21 9 3 6 12 2 12'/>"
    ),
    "Reports & Downloads": (
        "<path d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z'/>"
        "<polyline points='14 2 14 8 20 8'/>"
        "<line x1='16' y1='13' x2='8' y2='13'/>"
        "<line x1='16' y1='17' x2='8' y2='17'/>"
    ),
    "About & Help": (
        "<circle cx='12' cy='12' r='10'/>"
        "<path d='M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3'/>"
        "<line x1='12' y1='17' x2='12.01' y2='17'/>"
    ),
}


def _svg_url(body: str) -> str:
    raw = (
        "<svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' "
        "fill='none' stroke='black' stroke-width='2' stroke-linecap='round' "
        f"stroke-linejoin='round'>{body}</svg>"
    )
    return "data:image/svg+xml," + quote(raw)


def _inline_svg(body: str) -> str:
    if not body:
        return ""
    return (
        '<svg class="title-ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        f"{body}</svg>"
    )


_ICON_CSS = "\n".join(
    '[data-testid="stSidebar"] [role="radiogroup"] > :nth-child(%d) { --nav-icon: url("%s"); }'
    % (i, _svg_url(body))
    for i, body in enumerate(_NAV_ICONS.values(), start=1)
)

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
:root {{
  --navy: {THEME['navy_sidebar']};
  --navy-deep: {THEME['navy_dark']};
  --navy-hover: #0B3D73;
  --blue: {THEME['primary_blue']};
  --blue-hover: {THEME['blue_hover']};
  --blue-surface: {THEME['blue_surface']};
  --blue-soft: {THEME['blue_surface']};
  --teal: {THEME['teal']};
  --green: {THEME['green']};
  --amber: {THEME['amber']};
  --coral-red: {THEME['coral_red']};
  --purple: {THEME['purple']};
  --page-bg: {THEME['page_bg']};
  --surface: {THEME['card_bg']};
  --border: {THEME['border']};
  --muted-bg: {THEME['muted_bg']};
  --text-primary: {THEME['main_text']};
  --text-secondary: {THEME['secondary_text']};
  --text-muted: #8295A8;
  --risk-very-high: {THEME['risk_very_high']};
  --risk-high: {THEME['risk_high']};
  --risk-medium: {THEME['risk_medium']};
  --risk-low: {THEME['risk_low']};
  --radius-card: 10px;
  --radius-control: 6px;
  --shadow-card: 0 1px 3px rgba(8, 43, 82, 0.05), 0 1px 2px rgba(8, 43, 82, 0.03);
  --mute: var(--text-secondary);
  --ink: var(--text-primary);
  --font: 'Inter', "Segoe UI", system-ui, -apple-system, sans-serif;
}}
{_ICON_CSS}

  html, body, [class*="css"] {{ font-family: var(--font); }}
  .stApp {{
    background: var(--page-bg); color: var(--text-primary);
    font-family: var(--font); font-size: 14px;
  }}
  .block-container {{
    padding: 72px 28px 48px 28px !important; max-width: 1440px;
    container-type: inline-size;
  }}
  header[data-testid="stHeader"] {{ background: transparent; }}
  [data-testid="stToolbar"] {{ background: transparent; }}

  /* ── Sidebar ─────────────────────────────────────────────── */
  section[data-testid="stSidebar"] {{
    background: {THEME['navy_sidebar']} !important;
    border-right: 0;
  }}
  [data-testid="stSidebar"] [data-testid="stSidebarContent"] {{ padding: 4px 10px 16px; }}
  [data-testid="stSidebarHeader"] {{
    background: transparent !important; height: 48px !important; width: 100% !important;
    box-shadow: none !important;
  }}
  [data-testid="stSidebarCollapseButton"] button,
  [data-testid="stSidebarCollapseButton"] svg {{ color: #C8DAE8 !important; fill: currentColor; }}
  [data-testid="stSidebarHeader"] button,
  [data-testid="stSidebarCollapseButton"] button {{ color: #C8DAE8; }}

  .flag {{
    width: 28px; height: 18px; border-radius: 2px; flex: none;
    box-shadow: 0 0 0 1px rgba(0,0,0,0.18);
    background: linear-gradient(#2e9e4f 0 20%, #f2c230 0 35%, #d7261e 0 50%, #000 0 65%,
      #d7261e 0 80%, #f2c230 0 90%, #2e9e4f 0);
  }}
  .brand {{ display: flex; gap: 9px; align-items: center; margin: 8px 2px 16px; color: #fff; }}
  .brand b {{ display: block; font-size: 12.5px; line-height: 1.25; color: #fff; font-weight: 600; }}
  .brand small {{ display: block; font-size: 10.5px; color: #96B3C8; margin-top: 1px; }}
  .nav-label {{
    font-size: 10px; font-weight: 700; letter-spacing: 0.07em; text-transform: uppercase;
    color: #6E8CA0; margin: 2px 4px 6px;
  }}

  [data-testid="stSidebar"] [role="radiogroup"] {{ gap: 2px; }}
  [data-testid="stSidebar"] .stRadio > label {{ display: none; }}
  [data-testid="stSidebar"] [role="radiogroup"] label,
  [data-testid="stSidebar"] [data-baseweb="radio"] {{
    color: #C8DDE8 !important; font-size: 13px; font-weight: 500;
    padding: 9px 10px; margin: 0; border-radius: 4px;
    align-items: center; display: flex !important; gap: 10px; line-height: 1.3;
  }}
  [data-testid="stSidebar"] [role="radiogroup"] label::before,
  [data-testid="stSidebar"] [data-baseweb="radio"]::before {{
    content: ""; width: 15px; height: 15px; flex: none;
    background: currentColor;
    -webkit-mask: var(--nav-icon) center / contain no-repeat;
    mask: var(--nav-icon) center / contain no-repeat;
  }}
  [data-testid="stSidebar"] [data-baseweb="radio"] > div:first-child {{ display: none !important; }}
  [data-testid="stSidebar"] [role="radiogroup"] p {{ margin: 0; }}
  [data-testid="stSidebar"] [data-baseweb="radio"] * {{ color: inherit !important; }}
  [data-testid="stSidebar"] [role="radiogroup"] label:hover,
  [data-testid="stSidebar"] [data-baseweb="radio"]:hover {{
    background: rgba(255,255,255,0.06); color: #E8F2FA !important;
  }}
  [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked),
  [data-testid="stSidebar"] [data-baseweb="radio"]:has(input:checked) {{
    background: var(--blue) !important; color: #fff !important;
    border-radius: 6px !important;
  }}
  [data-testid="stSidebar"] [data-baseweb="radio"]:has(input:checked) * {{ color: #fff !important; font-weight: 600 !important; }}

  [data-testid="stSidebarContent"] > div.stVerticalBlock {{
    display: flex; flex-direction: column; min-height: calc(100vh - 96px);
  }}
  .proto {{
    margin-top: auto; background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.09); border-radius: 4px;
    padding: 10px 12px; font-size: 11px; color: #8DAFC5; line-height: 1.5;
  }}
  .proto b {{ color: #B8CDD8; display: block; margin-bottom: 3px; font-size: 11px; font-weight: 600; }}

  /* ── App-bar ─────────────────────────────────────────────── */
  .appbar {{
    display: flex; justify-content: space-between; align-items: center; gap: 16px;
    flex-wrap: wrap; padding: 12px 20px; margin: 0 0 20px 0;
    background: #082B52; border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(8, 43, 82, 0.14);
  }}
  .appbar-id {{ display: flex; align-items: center; gap: 12px; min-width: 0; }}
  .appbar-name strong {{
    display: block; font-size: 16px; line-height: 1.25; font-weight: 700;
    color: #FFFFFF; letter-spacing: -0.01em;
  }}
  .appbar-name span {{ display: block; font-size: 11.5px; color: #93C5FD; margin-top: 2px; }}
  .app-meta {{
    display: flex; gap: 16px; align-items: center; flex-wrap: wrap;
    background: rgba(255,255,255,0.08); padding: 6px 14px; border-radius: 6px;
    border: 1px solid rgba(255,255,255,0.12);
  }}
  .app-meta-item {{ font-size: 11.5px; color: #E2E8F0; text-align: right; }}
  .app-meta-item b {{
    display: inline-block; color: #FFFFFF; font-size: 12px; font-weight: 600; margin-left: 4px;
  }}

  /* ── Page title ──────────────────────────────────────────── */
  .top {{ margin: 0 0 20px 0; }}
  .top h1 {{
    font-size: 30px; display: flex; gap: 10px; align-items: center; margin: 0;
    color: var(--navy); font-weight: 700; letter-spacing: -0.02em; line-height: 1.25;
  }}
  .title-ic {{ width: 22px; height: 22px; color: var(--blue); flex: none; }}
  .top h1 i {{ font-style: normal; color: var(--blue); display: inline-flex; }}
  .top p {{ color: var(--text-secondary); font-size: 15px; margin: 5px 0 0 0; line-height: 1.5; }}

  .hdr {{ background: transparent; border: none; box-shadow: none; padding: 0; margin-bottom: 16px; }}
  .hdr-title {{ font-size: 24px; font-weight: 700; color: var(--navy); margin: 0; letter-spacing: -0.015em; }}
  .hdr-sub {{ font-size: 14px; color: var(--text-secondary); margin: 4px 0 0 0; line-height: 1.5; }}
  .hdr-prov {{ font-size: 12px; color: var(--text-muted); margin-top: 6px; }}

  /* ── Cards ───────────────────────────────────────────────── */
  .card {{
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius-card); padding: 18px 20px; height: 100%;
    box-sizing: border-box; box-shadow: var(--shadow-card);
  }}
  .card h3, h3.sec-title {{ font-size: 16px; font-weight: 700; color: var(--navy); margin: 0 0 6px 0; }}
  .card h4 {{ font-size: 14px; font-weight: 650; color: var(--navy); margin: 0 0 6px 0; }}
  .sec-sub {{ color: var(--text-secondary); font-size: 14px; margin: 3px 0 12px 0; line-height: 1.5; }}
  .sec-title {{ font-size: 20px; font-weight: 700; color: var(--navy); margin: 24px 0 8px 0;
    padding-bottom: 6px; border-bottom: 1px solid var(--border); letter-spacing: -0.01em; }}
  .cap {{ font-size: 12px; color: var(--text-muted); }}

  /* ── KPI / Metric ────────────────────────────────────────── */
  .stat, .metric-card {{ display: flex; gap: 0; align-items: flex-start; flex-direction: column; }}
  .metric-lbl {{ font-size: 12px; color: var(--text-secondary); font-weight: 650;
    text-transform: uppercase; letter-spacing: 0.05em; }}
  .metric-val {{
    font-size: 30px; font-weight: 700; color: var(--text-primary); line-height: 1.15;
    margin: 4px 0 3px 0; font-feature-settings: "tnum"; font-variant-numeric: tabular-nums;
  }}
  .metric-cap {{ font-size: 12.5px; color: var(--text-muted); line-height: 1.45; margin-top: 2px; }}

  /* ── Badges ──────────────────────────────────────────────── */
  .badge {{
    display: inline-flex; align-items: center; gap: 5px; padding: 2.5px 8px;
    border-radius: 4px; font-size: 11.5px; font-weight: 700; white-space: nowrap;
    letter-spacing: 0.03em; text-transform: uppercase; border: 1px solid transparent;
  }}
  .badge.very-high, .badge.r1 {{ background: #FEE2E2; color: #DC2626; border-color: #FECACA; }}
  .badge.high, .badge.r2, .badge.high-risk {{ background: #FFEDD5; color: #EA580C; border-color: #FED7AA; }}
  .badge.med, .badge.warn, .badge.r3 {{ background: #FEF3C7; color: #D97706; border-color: #FDE68A; }}
  .badge.low, .badge.ok, .badge.r4, .badge.r5 {{ background: #D1FAE5; color: #059669; border-color: #A7F3D0; }}
  .badge.info {{ background: #EAF3FF; color: var(--blue); border-color: #BFDBFE; }}
  .badge.res  {{ background: #F3E8FF; color: var(--purple); border-color: #DDD6FE; }}
  .badge.na   {{ background: var(--muted-bg); color: var(--text-secondary); border-color: var(--border); }}
  .badge.error {{ background: #FEE2E2; color: #DC2626; border-color: #FECACA; }}
  .badge.warning {{ background: #FEF3C7; color: #D97706; border-color: #FDE68A; }}

  .dot {{ width: 9px; height: 9px; border-radius: 999px; display: inline-block; flex: none; margin-top: 4px; }}
  .dot.very-high, .dot.r1 {{ background: var(--risk-very-high); }}
  .dot.high, .dot.r2, .dot.warn {{ background: var(--risk-high); }}
  .dot.med, .dot.r3 {{ background: var(--risk-medium); }}
  .dot.low, .dot.ok, .dot.r4, .dot.r5 {{ background: var(--risk-low); }}
  .dot.na {{ background: #9BAEBD; }}
  .dot.info {{ background: var(--blue); }}

  /* ── Tables ──────────────────────────────────────────────── */
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th {{
    text-align: left; color: var(--text-secondary); font-weight: 600; font-size: 11.5px;
    padding: 9px 8px; border-bottom: 1px solid var(--border); background: #F7FAFE;
    text-transform: uppercase; letter-spacing: 0.03em;
  }}
  td {{ padding: 9px 8px; border-bottom: 1px solid #EEF2F7; color: var(--text-primary); }}
  tbody tr:hover td {{ background: #F7FBFF; }}

  /* ── Info / note blocks ──────────────────────────────────── */
  .note {{
    background: #EBF3FF; border-radius: 4px; padding: 10px 14px;
    font-size: 13px; color: #0B4F86; border-left: 3px solid var(--blue);
  }}
  .lim {{ display: flex; gap: 10px; margin-bottom: 10px; align-items: flex-start; }}
  .lim b {{ display: block; font-size: 13px; color: var(--text-primary); font-weight: 600; }}
  .lim p {{ color: var(--text-secondary); font-size: 13px; margin: 2px 0 0 0; }}
  .empty {{
    text-align: center; padding: 32px 20px; color: var(--text-secondary);
    border: 1px dashed #C5D6E5; border-radius: var(--radius-card);
    font-size: 13px; background: #fff;
  }}
  .empty i {{ font-style: normal; font-size: 20px; display: block; color: #9BAEBD; margin-bottom: 8px; }}

  /* ── Pipeline stage list ─────────────────────────────────── */
  .stage {{
    display: flex; gap: 10px; align-items: flex-start;
    padding: 8px 2px; border-bottom: 1px solid #EEF2F7;
  }}
  .stage:last-child {{ border-bottom: 0; }}
  .stage-name {{ font-size: 13px; font-weight: 600; color: var(--text-primary); }}
  .stage-desc {{ font-size: 12px; color: var(--text-secondary); margin-top: 2px; line-height: 1.5; }}

  /* ── Insight rows ────────────────────────────────────────── */
  .insight {{
    display: flex; gap: 0; align-items: flex-start; padding: 8px 0;
    border-bottom: 1px solid #EEF2F7;
  }}
  .insight:last-child {{ border-bottom: 0; }}
  .insight-ic {{ display: none; }}
  .insight-tx {{ font-size: 13px; color: var(--text-primary); line-height: 1.5; }}

  /* ── Meta row ────────────────────────────────────────────── */
  div.meta {{
    background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-card);
    box-shadow: var(--shadow-card); margin-top: 16px; overflow: hidden;
  }}
  .cell {{ min-width: 120px; padding: 10px 14px; border-right: 1px solid var(--border); }}
  .cell:last-child {{ border-right: 0; }}
  .meta-l {{ font-size: 10.5px; color: var(--text-secondary); font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.04em; }}
  .meta-v {{ font-size: 13px; font-weight: 600; color: var(--text-primary); margin-top: 3px; }}
  .meta-c {{ font-size: 11px; color: var(--text-muted); margin-top: 1px; }}

  .btn {{
    display: inline-block; border: 1px solid var(--border); color: var(--text-primary);
    background: var(--surface); border-radius: var(--radius-control); padding: 6px 12px;
    font-size: 13px; font-weight: 500;
  }}
  code {{ background: #EEF3F8; color: var(--text-primary); border-radius: 4px; padding: 1px 5px; font-size: 12.5px; }}

  /* ── Form inputs ─────────────────────────────────────────── */
  [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label {{
    font-size: 12.5px !important; font-weight: 600 !important; color: #2A4A63 !important;
  }}
  div[data-baseweb="select"] > div,
  [data-baseweb="input"] > div,
  div[data-baseweb="base-input"] {{
    border: 1px solid #C0D0DF !important; border-radius: var(--radius-control) !important;
    background: #ffffff !important; min-height: 38px;
  }}
  div[data-baseweb="select"] > div:focus-within,
  [data-baseweb="input"]:focus-within > div,
  div[data-baseweb="base-input"]:focus-within {{
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 2px rgba(8,117,249,0.18) !important;
  }}
  input, textarea, [data-baseweb="input"] input, [data-baseweb="base-input"] input {{
    color: #17324D !important;
    -webkit-text-fill-color: #17324D !important;
    background-color: #ffffff !important;
    font-size: 13.5px !important;
    font-weight: 500 !important;
  }}
  input::placeholder, textarea::placeholder, [data-baseweb="input"] input::placeholder {{
    color: #8295A8 !important;
    -webkit-text-fill-color: #8295A8 !important;
    opacity: 1 !important;
    font-size: 13px !important;
  }}
  [data-baseweb="select"] * {{ color: #17324D !important; }}
  [data-testid="stNumberInput"] input,
  [data-testid="stTextInput"] input {{
    color: #17324D !important;
    -webkit-text-fill-color: #17324D !important;
    background-color: #ffffff !important;
    font-size: 13.5px !important; font-weight: 500 !important;
  }}
  [data-testid="stFileUploader"] section {{
    background: #fff; border: 1px dashed #C0D0DF; border-radius: 4px;
  }}

  /* ── Tabs ────────────────────────────────────────────────── */
  [data-baseweb="tab-list"] {{
    gap: 8px; background: transparent !important; border-radius: 0 !important;
    border-bottom: none !important; margin-bottom: 20px; padding: 0 !important;
  }}
  button[data-baseweb="tab"] {{
    background: #EAF3FF !important; border: 1px solid #DCE6F0 !important;
    border-radius: 6px !important;
    color: #1E3A8A !important; font-size: 13px !important;
    font-weight: 500 !important; padding: 7px 16px !important;
    transition: all 0.15s ease;
  }}
  button[data-baseweb="tab"][aria-selected="true"] {{
    color: #FFFFFF !important; border-color: var(--blue) !important;
    background: var(--blue) !important; font-weight: 600 !important;
    box-shadow: 0 2px 4px rgba(37,99,235,0.25) !important;
  }}
  button[data-baseweb="tab"]:hover {{
    background: #DBEAFE !important; color: var(--navy) !important;
  }}
  [data-baseweb="tab-border"] {{ display: none !important; }}
  [data-testid="stTabs"] [data-baseweb="tab-list"] {{ overflow-x: auto; }}

  /* ── Segmented control ───────────────────────────────────── */
  [data-testid="stSegmentedControl"] {{
    background: #F1F5F9 !important; border: 1px solid #E2E8F0 !important;
    border-radius: 8px !important; padding: 4px !important;
    margin: 0 0 20px 0; max-width: 100%;
  }}
  [data-testid="stSegmentedControl"] button {{
    border-radius: 6px !important; border: 0 !important; background: transparent !important;
    color: #475569 !important; font-size: 13px !important;
    font-weight: 500 !important; padding: 7px 16px !important;
  }}
  [data-testid="stSegmentedControl"] button[aria-checked="true"],
  [data-testid="stSegmentedControl"] button[aria-pressed="true"],
  button[data-testid="stBaseButton-segmented_controlActive"] {{
    background: var(--blue) !important; color: #FFFFFF !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 6px rgba(37,99,235,0.3) !important;
  }}
  button[data-testid="stBaseButton-segmented_control"] {{
    background: transparent !important; color: #475569 !important;
    border-color: transparent !important; font-weight: 500 !important;
  }}

  /* ── Buttons ─────────────────────────────────────────────── */
  .stButton > button,
  .stDownloadButton > button,
  button[data-testid="stBaseButton-secondary"] {{
    border-radius: var(--radius-control); border: 1px solid var(--border);
    background: var(--surface); color: var(--text-primary); font-weight: 500;
    padding: 6px 14px; font-size: 13px;
  }}
  .stButton > button:hover,
  .stDownloadButton > button:hover,
  button[data-testid="stBaseButton-secondary"]:hover {{
    background: #EBF3FF; border-color: var(--blue); color: var(--blue);
  }}
  .stButton > button[kind="primary"],
  button[data-testid="stBaseButton-primary"] {{
    background: var(--blue); color: #fff; border-color: var(--blue); font-weight: 600;
  }}
  .stButton > button[kind="primary"]:hover,
  button[data-testid="stBaseButton-primary"]:hover {{
    background: var(--blue-hover); border-color: var(--blue-hover); color: #fff;
  }}

  /* ── Alerts / expanders ──────────────────────────────────── */
  [data-testid="stAlert"] {{ border-radius: var(--radius-card); }}
  [data-testid="stExpander"] {{
    border-radius: var(--radius-card); border: 1px solid var(--border);
    background: #fff; box-shadow: var(--shadow-card);
  }}

  /* ── Chart card wrapper ──────────────────────────────────── */
  [class*="st-key-chartcard_"] {{
    background: var(--surface) !important; border: 1px solid var(--border) !important;
    border-radius: var(--radius-card) !important; padding: 12px 14px 6px !important;
    box-shadow: var(--shadow-card) !important;
  }}
  .card-title {{ font-size: 13px; font-weight: 600; color: var(--navy); margin: 0 0 6px 2px; }}
  [data-testid="stPlotlyChart"] {{ border: 0; }}
  [data-testid="stDataFrame"], [data-testid="stTable"] {{
    border: 1px solid var(--border) !important; border-radius: var(--radius-card) !important;
    overflow: hidden; background: var(--surface);
  }}

  /* ── Responsive ──────────────────────────────────────────── */
  @container (max-width: 980px) {{
    [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"]:nth-child(4)) {{
      flex-wrap: wrap !important;
    }}
    [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"]:nth-child(4)) > [data-testid="stColumn"] {{
      flex: 1 1 200px !important; min-width: 180px !important; width: auto !important;
      max-width: calc(50% - 8px) !important;
    }}
  }}
  @media (max-width: 900px) {{
    .block-container {{ padding: 68px 14px 32px !important; }}
    .appbar-name strong {{ font-size: 14px; }}
    .top h1 {{ font-size: 16px; }}
    .metric-val {{ font-size: 19px; }}
  }}
  @media (max-width: 720px) {{
    .appbar {{ align-items: flex-start; padding: 10px 12px; }}
    .app-meta-item {{ text-align: left; }}
    [data-testid="stHorizontalBlock"] {{ flex-wrap: wrap !important; }}
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {{
      width: 100% !important; flex: 1 1 100% !important; min-width: 100% !important;
    }}
  }}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def inject_legacy_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def esc(v) -> str:
    return html.escape(str(v))


# The section header lives in app.py; embedded pages must not render a second one.
_HEADER_ENABLED = True


def enable_page_header(flag: bool) -> None:
    global _HEADER_ENABLED
    _HEADER_ENABLED = flag


def sidebar_brand() -> None:
    """Sidebar brand header."""
    st.sidebar.markdown(
        '<div class="brand"><div class="flag" aria-hidden="true"></div><div>'
        '<b>Zimbabwe Food-Price Stress</b>'
        '<small>Early Warning ML System</small></div></div>'
        '<div class="nav-label">Navigation</div>',
        unsafe_allow_html=True)


def sidebar_disclaimer() -> None:
    st.sidebar.markdown(
        '<div class="proto"><b>Research prototype · Not for operational use</b>'
        'Predictions are experimental model outputs based on historical data.</div>',
        unsafe_allow_html=True)


def top(title: str, subtitle: str = "", icon: str = "",
        meta: Optional[Sequence[Tuple[str, str]]] = None) -> None:
    """App identity bar plus the current page title. Meta stays artefact-derived."""
    sub = f"<p>{esc(subtitle)}</p>" if subtitle else ""
    meta_html = ""
    if meta:
        cells = "".join(
            f'<span class="app-meta-item">{esc(k)}<b>{esc(v)}</b></span>' for k, v in meta
        )
        meta_html = f'<div class="app-meta">{cells}</div>'
    st.markdown(
        f'<header class="appbar"><div class="appbar-id"><div class="flag" aria-hidden="true"></div>'
        f'<div class="appbar-name"><strong>Zimbabwe Food-Price Stress</strong>'
        f'<span>Early Warning ML System</span></div></div>{meta_html}</header>'
        f'<div class="top"><h1>{esc(title)}</h1>{sub}</div>',
        unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "", provenance: str = "") -> None:
    if not _HEADER_ENABLED:
        return
    prov = f'<div class="hdr-prov">Source: {esc(provenance)}</div>' if provenance else ""
    st.markdown(
        f'<div class="hdr"><div class="hdr-title">{esc(title)}</div>'
        f'<div class="hdr-sub">{esc(subtitle)}</div>{prov}</div>',
        unsafe_allow_html=True)


def section(title: str, desc: str = "") -> None:
    d = f'<div class="sec-sub">{esc(desc)}</div>' if desc else ""
    st.markdown(f'<div class="sec-title">{esc(title)}</div>{d}',
                unsafe_allow_html=True)


def card(inner: str) -> None:
    st.markdown(f'<div class="card">{inner}</div>', unsafe_allow_html=True)


def kpi(label: str, value: str, caption: str = "", icon: str = "",
        color: str = "blue100", accent: str = "") -> str:
    cap = f'<div class="metric-cap" style="font-size:12px;color:#64748B;margin-top:2px;">{esc(caption)}</div>' if caption else ""
    tint_styles = {
        "blue": ("background:#EFF6FF; border:1px solid #BFDBFE;", "#1D4ED8"),
        "teal": ("background:#ECFDF5; border:1px solid #A7F3D0;", "#047857"),
        "green": ("background:#ECFDF5; border:1px solid #A7F3D0;", "#047857"),
        "amber": ("background:#FFFBEB; border:1px solid #FDE68A;", "#B45309"),
        "purple": ("background:#FAF5FF; border:1px solid #E9D5FF;", "#6D28D9"),
        "coral": ("background:#FEF2F2; border:1px solid #FECACA;", "#B91C1C"),
    }
    style_attr = ""
    val_color = "color:var(--navy);"
    if accent in tint_styles:
        card_bg, text_col = tint_styles[accent]
        style_attr = f' style="{card_bg}"'
        val_color = f"color:{text_col};"
    elif accent:
        acc_col = THEME.get(accent, accent)
        style_attr = f' style="border-top: 3px solid {acc_col};"'

    return (f'<div class="card"{style_attr}><div class="stat">'
            f'<div class="metric-lbl" style="font-size:12px;font-weight:600;color:#475569;text-transform:uppercase;letter-spacing:0.02em;">{esc(label)}</div>'
            f'<div class="metric-val" style="font-size:30px;font-weight:700;{val_color}margin:4px 0 2px;">{esc(value)}</div>{cap}'
            f'</div></div>')


def kpi_row(items: Iterable[dict]) -> None:
    items = list(items)
    if not items:
        return
    cols = st.columns(len(items), gap="small")
    for col, it in zip(cols, items):
        col.markdown(kpi(it["label"], it["value"], it.get("caption", ""),
                         it.get("icon", ""), it.get("color", "blue100"),
                         it.get("accent", "")),
                     unsafe_allow_html=True)


def badge(text: str, kind: str = "") -> str:
    cls = f"badge {kind}".strip()
    return f'<span class="{cls}">{esc(text)}</span>'


def note(text: str) -> None:
    st.markdown(f'<div class="note">{text}</div>', unsafe_allow_html=True)


def empty_state(title: str = "Nothing to show", sub: str = "", icon: str = "🗎") -> None:
    s = f"<br>{esc(sub)}" if sub else ""
    st.markdown(
        f'<div class="empty"><i>{icon}</i><b>{esc(title)}</b>{s}</div>',
        unsafe_allow_html=True)


def lim_row(icon: str, title: str, text: str) -> str:
    return (f'<div class="lim"><i>{icon}</i><div><b>{esc(title)}</b>'
            f'<p>{esc(text)}</p></div></div>')


def inject_css() -> None:
    css_path = Path(__file__).resolve().parents[1] / "styles" / "theme.css"
    try:
        css = css_path.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
        return
    except Exception:
        pass
    try:
        st.markdown(CSS, unsafe_allow_html=True)
    except Exception:
        pass


def provenance_caption(text: str) -> None:
    st.caption(f"Provenance: {text}")


def unavailable(what: str, path: str = "", note_: str = "") -> None:
    extra = f" Expected path: `{path}`." if path else ""
    tail = f" {note_}" if note_ else ""
    st.info(f"Not available in this environment: {what}.{extra}{tail}")


def risk_badge(p: float, prev: float) -> Tuple[str, str]:
    """Return (label, css-class) using documented 4-level risk scale."""
    if p >= max(prev * 2.2, prev + 0.20):
        return "Very high risk", "high"
    if p >= max(prev * 1.5, prev + 0.10):
        return "High risk", "high"
    if p >= prev:
        return "Medium risk", "med"
    return "Low risk", "ok"
