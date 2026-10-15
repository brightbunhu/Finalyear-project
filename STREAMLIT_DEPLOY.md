# Streamlit Cloud Deployment (quick guide)

1. Go to [share.streamlit.io](https://share.streamlit.io).
2. Sign in with GitHub and authorize Streamlit.
3. New App → Select repo `brightbunhu/LAst`.
4. Main file path: `dashboard/app.py`.
5. Python version: use the default (or 3.12) — the pinned dependencies in `requirements.txt` are compatible with 3.12 for this dashboard.
6. Deploy. Streamlit will install packages from `requirements.txt` and serve the app.

## Notes
- Data required at runtime: `data_processed/`, `artifacts/`, `models/`, `figures/`, `reports/`. These are committed (and < 25MB total). `raw/*.nc` (8.5GB) is excluded from the repo; no runtime dependency.
- `.streamlit/config.toml` is included (theme + settings).
- This is a research prototype; the dashboard reads only local artifacts produced by the pipeline.
- To refresh artifacts after running the pipeline: commit regenerated files and push to GitHub; Streamlit will redeploy.

## One-click later
Once deployed, the app URL will be: `https://brightbunhu-last.streamlit.app` (based on repo name `LAst`).
