"""Phase 1 profiling: inspect every supplied raw dataset without modifying it."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

LINES: list[str] = []


def log(*a):
    s = " ".join(str(x) for x in a)
    LINES.append(s)
    print(s)


def profile_csv(path: Path, name: str):
    log("=" * 100)
    log(f"FILE: {path.name}  ({path.stat().st_size/1e6:.2f} MB)")
    df = pd.read_csv(path, low_memory=False)
    log(f"shape: {df.shape[0]} rows x {df.shape[1]} cols")
    log("columns:")
    for c in df.columns:
        nn = df[c].notna().sum()
        miss = 100 * (1 - nn / len(df))
        nun = df[c].nunique(dropna=True)
        sample = df[c].dropna().head(3).tolist()
        log(f"   - {c!r:38} dtype={str(df[c].dtype):10} missing={miss:5.1f}%  unique={nun:>6}  e.g. {sample}")
    # date-like columns
    for c in df.columns:
        lc = c.lower()
        if "date" in lc or "period" in lc or lc == "date":
            try:
                d = pd.to_datetime(df[c], errors="coerce")
                log(f"   date[{c}] min={d.min()} max={d.max()} n_parsed={d.notna().sum()}")
            except Exception as e:  # noqa: BLE001
                log(f"   date[{c}] parse error {e}")
    return df


def main():
    # DataDetails workbook
    log("=" * 100)
    xls = RAW / "DataDetails.xls"
    log(f"WORKBOOK: {xls.name} ({xls.stat().st_size/1e6:.2f} MB)")
    try:
        xl = pd.ExcelFile(xls)
        log("sheets:", xl.sheet_names)
        for sn in xl.sheet_names:
            d = xl.parse(sn)
            log(f"--- sheet {sn!r}: {d.shape}")
            log("    columns:", list(d.columns))
            with pd.option_context("display.max_columns", 50, "display.width", 200):
                log(d.head(5).to_string())
    except Exception as e:  # noqa: BLE001
        log("Excel read error:", repr(e))

    for fn in [
        "wfp_markets_zwe.csv",
        "hdx_hapi_poverty_rate_zwe.csv",
        "hdx_hapi_population_zwe.csv",
        "hdx_hapi_rainfall_zwe.csv",
        "wfp_food_prices_zwe.csv",
        "hdx_hapi_food_price_zwe.csv",
    ]:
        try:
            profile_csv(RAW / fn, fn)
        except Exception as e:  # noqa: BLE001
            log(f"ERROR profiling {fn}: {e!r}")

    (REPORTS / "phase1_csv_profile.txt").write_text("\n".join(LINES), encoding="utf-8")
    print("\nwritten:", REPORTS / "phase1_csv_profile.txt")


if __name__ == "__main__":
    main()
