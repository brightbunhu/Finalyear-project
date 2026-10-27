"""Render PANEL_DEFENSE_DASHBOARD_GUIDE.html to PDF using Playwright with lock handling."""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML_FILE = ROOT / "PANEL_DEFENSE_DASHBOARD_GUIDE.html"
PRIMARY_PDF = ROOT / "PANEL_DEFENSE_DASHBOARD_GUIDE.pdf"
FALLBACK_PDF = ROOT / "PANEL_DEFENSE_DASHBOARD_GUIDE_UPDATED.pdf"

print(f"Loading {HTML_FILE}...")
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(f"file:///{HTML_FILE.as_posix()}", wait_until="networkidle")
    page.wait_for_timeout(1000)
    print("Rendering PDF...")
    
    target_pdf = PRIMARY_PDF
    try:
        page.pdf(
            path=str(target_pdf),
            format="A4",
            print_background=True,
            margin={"top": "12mm", "bottom": "12mm", "left": "10mm", "right": "10mm"}
        )
    except PermissionError:
        print(f"Primary file {PRIMARY_PDF.name} is locked by an open viewer. Writing to {FALLBACK_PDF.name}...")
        target_pdf = FALLBACK_PDF
        page.pdf(
            path=str(target_pdf),
            format="A4",
            print_background=True,
            margin={"top": "12mm", "bottom": "12mm", "left": "10mm", "right": "10mm"}
        )
    browser.close()

size = target_pdf.stat().st_size
print(f"SUCCESS: Generated PDF at {target_pdf} ({size:,} bytes)")
