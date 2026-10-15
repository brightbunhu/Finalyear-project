"""Capture screenshots of every dashboard page for Chapter 5.

Starts the Streamlit app headlessly, opens each page via its ?page= deep-link, waits
for it to render, and saves a full-page PNG into screenshots/.

Usage: python scripts/capture_dashboard.py
"""
from __future__ import annotations

import socket
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "screenshots"
OUT.mkdir(exist_ok=True)

PORT = 8765
PAGES = [
    "Overview",
    "Data coverage & quality",
    "Price trends",
    "Rainfall",
    "Market & commodity explorer",
    "Model performance",
    "Historical holdout predictions",
    "Prediction",
    "Geographic view",
    "Limitations & disclaimers",
]


def wait_port(port, timeout=120):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                return True
        except OSError:
            time.sleep(1)
    return False


def slug(name):
    return "".join(c if c.isalnum() else "_" for c in name).strip("_")


def main():
    cmd = [sys.executable, "-m", "streamlit", "run", "dashboard/app.py",
           "--server.headless", "true", "--server.port", str(PORT),
           "--browser.gatherUsageStats", "false"]
    proc = subprocess.Popen(cmd, cwd=str(ROOT))
    try:
        if not wait_port(PORT):
            print("Streamlit did not start in time"); return
        time.sleep(6)
        base = f"http://127.0.0.1:{PORT}/"
        op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        try:
            op.open(base, timeout=10).read()
        except Exception:
            pass

        from playwright.sync_api import sync_playwright

        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page(viewport={"width": 1600, "height": 1000},
                                    device_scale_factor=2)
            for name in PAGES:
                url = base + "?" + urllib.parse.urlencode({"page": name})
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=60000)
                except Exception as e:
                    print(f"goto warning for {name}: {type(e).__name__}")
                try:
                    page.wait_for_selector('[data-testid="stAppViewContainer"]',
                                           timeout=60000)
                except Exception:
                    pass
                time.sleep(10)
                f = OUT / f"{slug(name)}.png"
                page.screenshot(path=str(f), full_page=True)
                print(f"saved {f.name}")
            browser.close()
        print(f"\nAll screenshots in {OUT}")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=15)
        except Exception:
            proc.kill()


if __name__ == "__main__":
    main()
