"""Launch Streamlit dashboard in background, capture screenshots using Playwright, and save images."""
import os
import subprocess
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT_SHOTS = ROOT / "outputs" / "figures" / "screenshots"
ROOT_SHOTS = ROOT / "screenshots"
OUT_FIG = ROOT / "outputs" / "figures"

OUT_SHOTS.mkdir(parents=True, exist_ok=True)
ROOT_SHOTS.mkdir(parents=True, exist_ok=True)

PORT = 8501
URL = f"http://localhost:{PORT}"

print("Starting Streamlit process...")
env = os.environ.copy()
env["PYTHONPATH"] = str(ROOT / "dashboard") + os.pathsep + env.get("PYTHONPATH", "")

proc = subprocess.Popen(
    ["streamlit", "run", "dashboard/app.py", "--server.port", str(PORT), "--server.headless", "true"],
    cwd=str(ROOT),
    env=env,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)

# Wait for server to start
import urllib.request
started = False
for i in range(25):
    time.sleep(1)
    try:
        urllib.request.urlopen(URL, timeout=2)
        started = True
        print(f"Streamlit server is up and responsive at {URL}")
        break
    except Exception:
        print(f"Waiting for Streamlit server... ({i+1}/25)")

if not started:
    print("Streamlit server failed to start in time.")
    proc.terminate()
    exit(1)

# Playwright capture
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1600, "height": 1050})

        pages_to_capture = [
            ("Home", "dashboard_01_home.png", "Home Overview Page"),
            ("Make a Prediction", "dashboard_02_prediction_studio.png", "Scenario Prediction Studio"),
            ("Geographic Explorer", "dashboard_03_geographic_explorer.png", "Geographic Explorer Page"),
            ("Data & Integration", "dashboard_04_dataset_catalogue.png", "Data & Integration Overview"),
            ("Coverage & Quality", "dashboard_05_coverage_quality.png", "Data Coverage & Quality Page"),
            ("Price Trends", "dashboard_06_price_trends.png", "Commodity Price Trends Page"),
            ("Rainfall & Climate", "dashboard_07_rainfall_climate.png", "Rainfall & Climate Anomaly Page"),
            ("Model Performance", "dashboard_08_model_performance.png", "Model Performance Overview"),
            ("Holdout Predictions", "dashboard_09_historical_holdout.png", "Holdout Predictions Page"),
            ("Statistical Analysis", "dashboard_10_statistical_analysis.png", "Statistical Analysis Page"),
            ("Research Evidence", "dashboard_11_research_evidence.png", "Research Evidence & Downloads"),
            ("Limitations & Interpretation", "dashboard_12_limitations.png", "Limitations & Academic Scope"),
        ]

        for page_name, filename, desc in pages_to_capture:
            print(f"Capturing: {desc} ({filename})...")
            # Navigate using legacy page routing parameter
            target_url = f"{URL}/?page={page_name.replace(' ', '+').replace('&', '%26')}"
            page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(4.0)  # Allow Streamlit components and charts to fully render

            # Save in multiple destinations
            p1 = OUT_SHOTS / filename
            p2 = ROOT_SHOTS / filename
            p3 = OUT_FIG / filename
            page.screenshot(path=str(p1), full_page=False)
            page.screenshot(path=str(p2), full_page=False)
            page.screenshot(path=str(p3), full_page=False)
            print(f"  Saved {filename}")

        browser.close()
        print("Playwright capture completed successfully.")

finally:
    print("Terminating Streamlit server process...")
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except Exception:
        proc.kill()
    print("Streamlit process stopped.")
