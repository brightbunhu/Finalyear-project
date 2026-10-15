# Phase 1 — Inventory, Dataset Dictionary and Source Register

Project: **Machine Learning Based Food Price Stress Prediction in Zimbabwe Using XGBoost**
Prepared: Phase 1 (evidence-based rebuild). All figures below were produced by
`scripts/phase1_*.py` against the files in `raw/`. Nothing in this document is
copied from the dissertation's results chapters.

---

## 1. Complete file inventory

| # | Path | Size | Type | Content (verified) |
|---|------|------|------|--------------------|
| 1 | `Chapter 1-5.docx` | 1.02 MB | Word | Dissertation, Chapters 1–5. 324 paragraphs, 7 tables, 4 embedded figures (image2–image5 PNG + image1 JPEG logo). **Empty bibliography** (a "References" heading with no entries). No tracked comments, no footnotes/endnotes, no supervisor feedback inside the file. |
| 2 | `raw/wfp_food_prices_zwe.csv` | 3.66 MB | CSV | 28,168 rows × 16 cols. Primary market price panel. Date range **2010-01-15 → 2026-05-15**. |
| 3 | `raw/wfp_markets_zwe.csv` | 0.03 MB | CSV | 486 rows × 7 cols. Market reference (id, name, admin1, admin2, lat, lon). Covers 486 markets; only 336 appear in the price file. |
| 4 | `raw/hdx_hapi_food_price_zwe.csv` | 4.61 MB | CSV | 25,554 rows × 22 cols. HDX HAPI harmonised version of the WFP price data. Date range **2017-01-15 → 2026-05-15** (i.e. a shorter, re-coded subset of #2). |
| 5 | `raw/hdx_hapi_rainfall_zwe.csv` | 0.67 MB | CSV | 5,100 rows × 20 cols. **Admin-1 (province) only**, `admin_level=1`. 2022-01 → 2026-09. Aggregation periods: `dekad`, `1-month`, `3-month`. Derived from CHIRPS. |
| 6 | `raw/hdx_hapi_population_zwe.csv` | 0.65 MB | CSV | 5,508 rows × 17 cols. Admin-0/1/2 population disaggregated by sex and age. Single reference period **2023**. |
| 7 | `raw/hdx_hapi_poverty_rate_zwe.csv` | 3.8 KB | CSV | 33 rows × 14 cols. **Admin-0/1 only**. MPI, headcount ratio, etc. 3 periods (2010/11, 2015, 2019). |
| 8 | `raw/yr.nc` | 8.94 GB | NetCDF4 | **CHIRPS v3.0 monthly precipitation**, global, 0.05° (2400×7200), `time` = **548 months, 1981-01 → 2026-08**. Variable `precip` (mm/month). This is the only source capable of true district-level (admin-2) rainfall. |
| 9 | `raw/geo/zwe_adm1_geoboundaries.geojson` | 7.24 MB | GeoJSON | 10 admin-1 polygons (geoBoundaries, ZIMSTAT/OCHA source, 2020 boundaries). |
| 10 | `raw/geo/zwe_adm2_geoboundaries.geojson` | 17.38 MB | GeoJSON | 91 admin-2 polygons (districts). |
| 11 | `raw/geo/zwe_adm1_metadata.json`, `zwe_adm2_metadata.json` | 2 KB each | JSON | geoBoundaries provenance/licence (CC BY 3.0 IGO). |
| 12 | `raw/DataDetails.xls` | 0.68 MB | XLS | **Unrelated to this project.** World Bank *Enterprise Surveys* "Data Details" workbook (Afghanistan, Cabo Verde, Cameroon …). Likely included in error. |

Machine-readable profiles produced in Phase 1:
`reports/phase1_csv_profile.txt`, `reports/phase1_nc_geo_profile.txt`,
`reports/phase1_food_deep.txt`, `reports/phase1_feasibility.txt`.

---

## 2. Dataset dictionary

### 2.1 `wfp_food_prices_zwe.csv` (primary price panel)

| Column | Type | Missing | Notes |
|--------|------|---------|-------|
| `date` | datetime | 0% | Always day **15** (monthly snapshot). 192 distinct months. |
| `admin1` | text | 3.2% | 10 provinces. |
| `admin2` | text | 3.2% | 81 districts; 907 rows (8 markets) have no district. |
| `market` | text | 0% | 336 markets. |
| `market_id` | int | 0% | 336 ids. |
| `latitude`, `longitude` | float | 3.2% | 235/237 distinct values. |
| `category` | text | 0% | 6 values **including `non-food`**. |
| `commodity` | text | 0% | 31 values (incl. fuel, soap, toothpaste). |
| `commodity_id` | int | 0% | 31 ids. |
| `unit` | text | 0% | `KG`, `L`, `100 ML`, `250 G`. |
| `priceflag` | text | 0% | `aggregate` (21,989) vs `actual` (6,179). |
| `pricetype` | text | 0% | `Retail` only (100%). |
| `currency` | text | 0% | `ZWL` (22,153) / `USD` (6,015). |
| `price` | float | 0% | Nominal price. min 0.13, max 266,553.88. No ≤0 values. |
| `usdprice` | float | 0% | Converted price. min **0.000015** (suspiciously small). |

Coverage by year (rows): sparse 2010–2018 (207–1,160/yr); 2019 = 181;
**2020 = 8,551; 2021 = 5,621; 2022 = 2,509; 2023 = 4,686**; 2024 = 1,785;
2025 = 611; 2026 = 196.

Currency regime (verified from data, **not** from the dissertation):
- 2010–2018: **USD only**
- 2019–2022: **ZWL only** (a handful of USD in 2021)
- 2023–2026: **mixed** USD/ZWL, USD-dominant from 2024

### 2.2 `wfp_markets_zwe.csv`

`market_id` (486 unique), `market`, `countryiso3` (all ZWE), `admin1` (10, 1.6% missing),
`admin2` (81, 1.6% missing), `latitude`/`longitude` (1.6% missing).
This is the authoritative market→district crosswalk. All 336 price-file `market_id`s
are present here.

### 2.3 `hdx_hapi_food_price_zwe.csv`

A re-coded harmonisation of the WFP prices with **P-codes** (`admin1_code` ZW10…,
`admin2_code` ZW1103…), `provider_admin1_name`/`provider_admin2_name`, `market_name`,
`lat`/`lon`, `commodity_category` (6), `commodity_name` (28), `unit`, `price_flag`,
`price_type` (Retail), `currency_code`, `price`, `reference_period_start/_end`.
Covers **2017-01 → 2026-05** only. Useful as (a) a source of P-codes to build the
market→district crosswalk and (b) a cross-check. 0.8% missing admin codes.

### 2.4 `hdx_hapi_rainfall_zwe.csv`

Granularity **admin-1 only**. Fields: `admin1_code/name`, `aggregation_period`
(`dekad`/`1-month`/`3-month`), `rainfall`, `rainfall_long_term_average`,
`rainfall_anomaly_pct`, `number_pixels` (fixed 18/pixel count per province),
`version` (`final`), reference period. Range 2022-01 → 2026-09.
**Cannot** produce district rainfall. Superseded for this project by `yr.nc`.

### 2.5 `hdx_hapi_population_zwe.csv`

`admin_level` ∈ {0,1,2}, `gender` ∈ {f,m,all}, `age_range` (18 bands),
`population`, single period 2023. Gives district (admin-2) population for 91 units.

### 2.6 `hdx_hapi_poverty_rate_zwe.csv`

Admin-0/1 only; `mpi`, `headcount_ratio`, `intensity_of_deprivation`,
`vulnerable_to_poverty`, `in_severe_poverty`; 3 non-contiguous periods.

### 2.7 `yr.nc` (CHIRPS v3.0)

`precip[time, latitude, longitude]`, units mm/month, 0.05°, global,
1981-01 → 2026-08. Verified Zimbabwe extract (lat −23..−15, lon 25..33.5) returns
valid values (Jan-2020 mean ≈ 134 mm, range 17.5–324.6 mm, 0% NaN). **This is the
defensible rainfall source for district-level (admin-2) anomalies.**

---

## 3. Data-source register (provenance)

| Dataset | Provider / provenance | Documentation available | Licence / notes |
|---------|----------------------|-------------------------|-----------------|
| WFP food prices | UN World Food Programme (VAM market monitoring), distributed via HDX (`data.humdata.org`). Confirmed by identical commodity/units in the HAPI file. | Column semantics only; **no accompanying codebook supplied**. | Public HDX dataset. Exact licence text **not supplied** — to be confirmed from the HDX page. |
| HDX HAPI datasets (food price, rainfall, population, poverty) | OCHA HDX HAPI harmonisation layer. | Column names self-describing; `provider_*`/`admin*_code` fields present. | Public. Version/reference periods present per row. |
| `yr.nc` | **CHIRPS v3.0**, Climate Hazards Center, UCSB; `data_created 2026-09-11`. Global attrs cite Funk et al. (2014/2015). | Full global attributes embedded in the file. | Open; cite Funk et al. |
| Administrative boundaries | geoBoundaries (William & Mary), source ZIMSTAT/OCHA ROSEA, 2020 boundaries, build Dec 2023. | `*_metadata.json` present. | CC BY 3.0 IGO. |
| `DataDetails.xls` | World Bank Enterprise Surveys. | n/a | **Not part of this project.** |

Unresolved provenance questions: (a) exact WFP VAM licence and the meaning of
`priceflag = "aggregate"`; (b) whether `usdprice` for ZWL rows uses official or
parallel FX; (c) CHIRPS `precip` global attrs say "convective precipitation rate"
though units are mm/month and the title is CHIRPS — a metadata inconsistency worth noting.

---

## 4. What the data can and cannot support (feasibility)

**Feasible**
- A **market × commodity × currency × month** panel. Verified size: **20,530 food
  cells** after removing `non-food` and keeping `price>0` (28,168 → 20,530).
- Log returns, lags, rolling returns **within each (market, commodity, currency)
  series** (3,029 series).
- **District-level rainfall anomalies** from `yr.nc` via zonal statistics on the 91
  admin-2 polygons (CHIRPS monthly covers the whole period).
- Peer-market comparisons (same commodity + currency, same month).
- Seasonality (month sin/cos), commodity group, currency regime.
- District population (2023) and province poverty (3 periods) as static context.

**Feasible but weak (must be reported as a limitation)**
- **Supervised next-month targets.** Only **7,624 cells (37.1%)** have an
  immediately-following monthly observation, and series are short: median series
  length = **4 months**; only **108 series have ≥24 months**, **38 have ≥36**, **0
  have ≥120**. This is a *short-panel* problem; many series will contribute 1–3 labels.
- Pre-2019 coverage is thin and USD-only; 2019 has only 94 food cells.

**Not feasible / must not be claimed**
- The dissertation's "3,571 primary observations / 607 positives (17.0%)" and
  "10,459 SPI observations / 1,300 positives (12.43%)" **cannot be reproduced from
  the supplied raw files** (no such artefacts exist). They are unverified.
- District rainfall from `hdx_hapi_rainfall_zwe.csv` (admin-1 only) — must use `yr.nc`.
- Any claim about `food_prices_zwe_core.parquet`, `adm2_monthly_rainfall.parquet`,
  `market_admin_crosswalk.csv`, `live_prediction.py`, `map_stress.py` — **none of
  these files exist**. Every implementation claim in Chapters 3–5 is currently
  unsupported by artefacts.

**Infeasible inputs named in the dissertation** but absent from the raw data:
temperature, soil moisture, vegetation/NDVI, crop yields, fuel prices (only 82 rows
for diesel/petrol each, non-food), border data, informal FX rates, household surveys.
The `scope`/`limitations` sections already exclude these; that exclusion is honest
and should stay.

---

## 5. Prioritised plan (Phase 2 onward)

1. **Phase 2 — Target definition.** Decide currency handling (recommend: analyse USD
   and ZWL regimes separately, or use `usdprice` for a currency-comparable series and
   test both), the standardisation reference (commodity×currency, using a *trailing*
   window), the stress threshold, and the prediction horizon. Separate tasks for
   (A) standardised-return stress and (B) peer-relative SPI stress.
2. **Phase 3 — Build the reproducible pipeline** (`src/`): clean → aggregate →
   crosswalk markets to districts → zonal CHIRPS → features with strict availability
   cut-offs → labels → saved parquet + processing log.
3. **Phase 4 — EDA** on the real panel; regenerate the figures referenced by Chapters 3–4.
4. **Phase 5 — Models**: majority, persistence, elastic-net logistic, XGBoost,
   histogram GBM; expanding-window CV + forward holdout; full metric set.
5. **Phases 6–10** as specified.

Open decisions requiring your input are listed in
`reports/phase1_missing_information.md`.
