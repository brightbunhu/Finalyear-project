"""Phase 3 - build the market x commodity x currency x month panel.

Steps: load & clean WFP prices -> exclude non-food -> aggregate to monthly median
per (market, commodity, currency) -> crosswalk markets to admin-2 districts by
point-in-polygon -> merge CHIRPS district-month rainfall anomalies -> merge 2023
district population -> build price features, rainfall features, seasonality, and
the two targets defined in config/targets.yml. One panel is produced per price base.

Outputs:
  data_processed/market_admin_crosswalk.csv
  data_processed/panel_nominal_within_currency.parquet
  data_processed/panel_usdprice.parquet
  data_processed/panel_build_log.txt
"""
from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import yaml
from shapely.geometry import Point

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw"
OUT = ROOT / "data_processed"
REP = ROOT / "reports"
OUT.mkdir(exist_ok=True)
CFG = yaml.safe_load((ROOT / "config" / "targets.yml").read_text(encoding="utf-8"))
L: list[str] = []


def log(*a):
    s = " ".join(str(x) for x in a)
    L.append(s)
    print(s)


# ------------------------------------------------------------------ crosswalk
def build_crosswalk(price_markets: pd.DataFrame) -> pd.DataFrame:
    adm2 = gpd.read_file(RAW / "geo" / "zwe_adm2_geoboundaries.geojson")[["shapeName", "geometry"]]
    adm2 = adm2.rename(columns={"shapeName": "district_geo"}).set_crs(4326, allow_override=True)
    adm1 = gpd.read_file(RAW / "geo" / "zwe_adm1_geoboundaries.geojson")[["shapeName", "geometry"]]
    adm1 = adm1.rename(columns={"shapeName": "admin1_geo"}).set_crs(4326, allow_override=True)

    m = price_markets.copy()
    has_xy = m["latitude"].notna() & m["longitude"].notna()
    pts = gpd.GeoDataFrame(
        m[has_xy].copy(),
        geometry=[Point(x, y) for x, y in zip(m.loc[has_xy, "longitude"], m.loc[has_xy, "latitude"])],
        crs=4326,
    )
    j2 = gpd.sjoin(pts, adm2, how="left", predicate="within").drop(columns="index_right")
    j2 = j2[~j2.index.duplicated()]
    j1 = gpd.sjoin(pts, adm1, how="left", predicate="within")[["admin1_geo"]]
    j1 = j1[~j1.index.duplicated()]
    res = j2.join(j1)
    m["district_geo"] = res["district_geo"]
    m["admin1_geo"] = res["admin1_geo"]
    m["xy_present"] = has_xy
    # flag: reported admin2 equals geo district (case-insensitive)
    rep = m["admin2"].fillna("").str.lower().str.strip()
    geo = m["district_geo"].fillna("").str.lower().str.strip()
    m["district_name_match"] = (rep == geo) & (rep != "")
    return m.reset_index(drop=True)


def norm(s):
    return (s.astype(str).str.lower().str.strip()
            .str.replace(r"[^a-z0-9 ]", "", regex=True)
            .str.replace(r"\s+", " ", regex=True))


# ------------------------------------------------------------------ population
def district_population() -> pd.DataFrame:
    pop = pd.read_csv(RAW / "hdx_hapi_population_zwe.csv")
    p2 = pop[(pop["admin_level"] == 2) &
             (pop["gender"].astype(str).str.lower() == "all") &
             (pop["age_range"].astype(str).str.lower() == "all")].copy()
    p2 = p2[["admin2_code", "admin2_name", "population"]].dropna(subset=["admin2_code"])
    p2["district_norm"] = norm(p2["admin2_name"])
    p2 = p2.groupby("district_norm", as_index=False)["population"].max()
    return p2


# ------------------------------------------------------------------ features
def build_base(panel_keys: pd.DataFrame, value_col: str, base_name: str,
               rain: pd.DataFrame, pop_match: dict) -> pd.DataFrame:
    df = panel_keys.copy().sort_values(["market_id", "commodity_id", "currency", "month"]).reset_index(drop=True)
    tr = CFG["target_return_stress"]
    win = int(tr["trailing_window_months"])
    minp = int(tr["min_prior_returns"])
    thr = float(tr["threshold_sd"])

    # ---- peer SPI (global by commodity+currency+month)
    tp = CFG["target_peer_stress"]
    grp = ["commodity_id", "currency", "month"]
    peer = df.groupby(grp)[value_col].agg(peer_median="median", peer_count="size").reset_index()
    df = df.merge(peer, on=grp, how="left")
    df["spi"] = df[value_col] / df["peer_median"]
    df.loc[df["peer_count"] < int(tp["min_peer_markets"]), "spi"] = np.nan

    # ---- return + trailing stats per series
    def per_series(g: pd.DataFrame) -> pd.DataFrame:
        g = g.sort_values("month")
        r = np.log(g[value_col]).diff()
        m = g["month"]
        # invalidate returns across month gaps
        gap = (m - m.shift(1)).dt.days
        r = r.where(gap.between(28, 31))
        out = pd.DataFrame(index=g.index)
        out["ret"] = r
        out["ret_lag1"] = r.shift(1).where((m - m.shift(1)).dt.days.between(28, 31))
        out["ret_lag2"] = r.shift(2).where((m - m.shift(2)).dt.days.between(59, 62))
        out["ret_roll3"] = r.rolling(3, min_periods=2).mean()
        # stats available strictly before t (for current-return feature)
        mu_prev = r.rolling(win, min_periods=minp).mean().shift(1)
        sd_prev = r.rolling(win, min_periods=minp).std().shift(1)
        out["ret_z_cur"] = (r - mu_prev) / sd_prev
        # stats through t (for the future-return label)
        mu_cur = r.rolling(win, min_periods=minp).mean()
        sd_cur = r.rolling(win, min_periods=minp).std()
        n_prior = r.notna().cumsum()
        next_r = r.shift(-1).where((m.shift(-1) - m).dt.days.between(28, 31))
        z_next = (next_r - mu_cur) / sd_cur
        out["z_next"] = z_next
        out["y1"] = np.where(z_next.notna(), (z_next >= thr).astype(float), np.nan)
        out["labelable_y1"] = z_next.notna() & (sd_cur > 0)
        # next-month peer SPI label
        next_spi = g["spi"].shift(-1).where((m.shift(-1) - m).dt.days.between(28, 31))
        out["next_spi"] = next_spi
        out["y2"] = np.where(next_spi.notna(), (next_spi >= float(tp["threshold_spi"])).astype(float), np.nan)
        out["labelable_y2"] = next_spi.notna()
        return out

    feats = df.groupby(["market_id", "commodity_id", "currency"], group_keys=False).apply(per_series)
    df = df.join(feats)

    # ---- rainfall features by district-month
    df["cal_month"] = df["month"].dt.month
    df["month_sin"] = np.sin(2 * np.pi * df["cal_month"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["cal_month"] / 12)
    df = df.merge(rain, left_on=["district", "month"], right_on=["district_geo", "month"], how="left")

    # ---- population
    df["district_norm"] = norm(df["district"])
    df["population"] = df["district_norm"].map(pop_match)
    df["log_population"] = np.log(df["population"])

    df["price_base"] = base_name
    return df


def main():
    log("Phase 3 panel build")
    prices = pd.read_csv(RAW / "wfp_food_prices_zwe.csv")
    log(f"raw price rows: {len(prices)}")
    prices["date"] = pd.to_datetime(prices["date"])
    prices["month"] = prices["date"].dt.to_period("M").dt.to_timestamp()

    inc = set(CFG["categories"]["include"])
    before = len(prices)
    prices = prices[prices["category"].isin(inc)].copy()
    log(f"after food-category filter: {len(prices)} (removed {before-len(prices)} non-food/other)")
    prices = prices[prices["price"] > 0].copy()
    log(f"after price>0: {len(prices)}")

    markets = (prices.sort_values("date")
               .groupby("market_id")
               .agg(market=("market", "last"), admin1=("admin1", "last"),
                    admin2=("admin2", "last"), latitude=("latitude", "last"),
                    longitude=("longitude", "last"))
               .reset_index())
    cross = build_crosswalk(markets)
    cross.to_csv(OUT / "market_admin_crosswalk.csv", index=False)
    log(f"markets: {len(cross)}  with geo district: {cross['district_geo'].notna().sum()}  "
        f"name match to reported admin2: {int(cross['district_name_match'].sum())}  "
        f"no coords: {(~cross['xy_present']).sum()}")
    missing_districts = sorted(cross.loc[cross['district_geo'].isna(), 'market'].tolist())
    log("markets without a geo district:", missing_districts)

    # ---- monthly median per market-commodity-currency
    key = ["market_id", "commodity_id", "currency", "month"]
    panel = (prices.groupby(key, dropna=False)
             .agg(price=("price", "median"), usdprice=("usdprice", "median"),
                  n_records=("price", "size"),
                  unit=("unit", lambda s: s.mode().iat[0]),
                  category=("category", lambda s: s.mode().iat[0]),
                  admin1=("admin1", "last"), admin2=("admin2", "last"),
                  priceflag_any_aggregate=("priceflag", lambda s: bool((s == "aggregate").any())))
             .reset_index())
    log(f"monthly cells (market-commodity-currency-month): {len(panel)}")
    panel = panel.merge(cross[["market_id", "district_geo", "admin1_geo", "district_name_match"]],
                        on="market_id", how="left")
    panel = panel.rename(columns={"district_geo": "district", "admin1_geo": "province_geo"})

    # ---- rainfall table with lags + rolling sum
    rain = pd.read_parquet(OUT / "rainfall_district_month_anom.parquet")
    rain = rain.sort_values(["district", "month"])
    rain["rain_anom_lag1"] = rain.groupby("district")["rainfall_anom_z"].shift(1)
    rain["rain_anom_lag2"] = rain.groupby("district")["rainfall_anom_z"].shift(2)
    rain["rain_anom_lag3"] = rain.groupby("district")["rainfall_anom_z"].shift(3)
    rain["rain_roll3_mm"] = (rain.groupby("district")["rainfall_mm"]
                             .rolling(3, min_periods=2).sum().reset_index(level=0, drop=True))
    rain = rain.rename(columns={"district": "district_geo", "rainfall_anom_z": "rain_anom_z"})

    pop = district_population()
    pop_match = dict(zip(pop["district_norm"], pop["population"]))
    log(f"population districts available: {len(pop_match)}")

    for base in CFG["price_bases"]:
        df = build_base(panel, base["value_column"], base["name"], rain, pop_match)
        fn = OUT / f"panel_{base['name']}.parquet"
        df.to_parquet(fn, index=False)
        n1 = int(df["labelable_y1"].sum()); p1 = int((df["y1"] == 1).sum())
        n2 = int(df["labelable_y2"].sum()); p2 = int((df["y2"] == 1).sum())
        log(f"[{base['name']}] rows={len(df)}  "
            f"y1 labelable={n1} pos={p1} ({100*p1/max(n1,1):.2f}%)  "
            f"y2 labelable={n2} pos={p2} ({100*p2/max(n2,1):.2f}%)")
        log(f"   saved {fn.name}")

    (OUT / "panel_build_log.txt").write_text("\n".join(L), encoding="utf-8")
    print("done")


if __name__ == "__main__":
    main()
