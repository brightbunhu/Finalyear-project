# Phase 1 — Data Quality Report

All statements below were verified against the raw files by `scripts/phase1_*.py`.
Where a value is uncertain, it is marked **[unverified]** rather than assumed.

---

## 1. Completeness / missingness

| Dataset | Key missingness |
|---------|-----------------|
| WFP prices | `admin1`/`admin2`/lat/lon missing in **907 rows (3.2%)** = 8 markets. No missing `price`, `currency`, `commodity`, `unit`, `date`. |
| WFP markets | `admin1`/`admin2`/coords missing in 1.6% of markets. |
| HAPI food price | admin codes missing in **0.8%**. |
| HAPI rainfall | `admin2_*` **100% missing** (admin-1 product). |
| HAPI population | `admin2_*` missing 10.8% (only national/province rows). |
| HAPI poverty | admin-1 only; 9.1% national rows. |
| CHIRPS `yr.nc` | Zimbabwe window: 0% NaN (verified). |

## 2. Duplicates

- **Full-row duplicates in WFP prices: 0.**
- Duplicates on `(date, market_id, commodity_id, currency, unit, pricetype, priceflag): 0.**
- Every `(market_id, commodity_id, currency, month)` tuple is unique (20,530 food
  cells from 20,530 food rows) → **no within-month collisions**, so a monthly
  aggregation rule mainly protects against future changes rather than current data.

## 3. Units, currencies, measurement consistency

- **Units are mixed across commodities but consistent within commodity** on
  inspection, EXCEPT the codes to watch: `KG`, `L`, `100 ML`, `250 G`. Non-food items
  (soap, toothpaste, fuel) use `250 G`/`100 ML`/`L`.
- **Two currencies, cleanly separated in time** (see §5). ZWL dominates 2019–2023;
  USD dominates 2010–2018 and 2024–2026. This is the single largest source of
  **non-comparability**: nominal ZWL prices rose by orders of magnitude for reasons
  unrelated to food scarcity.

## 4. Suspicious / unusual observations

- `usdprice` minimum = **0.000015** (≈ 1.5×10⁻⁵ USD). Implausible as a real USD
  shelf price; indicates either an extreme ZWL nominal divided by an official FX rate,
  or a data-entry issue. **Rows must be inspected individually before use [unverified].**
- `price` maximum = **266,553.88** (ZWL era) — consistent with hyperinflation, not a
  typo, but it dominates any nominal-price scale.
- The `priceflag` field is `aggregate` for **78% of rows** vs `actual` for 22%.
  The WFP meaning of "aggregate" **[unverified]** — must be confirmed before use; if
  it denotes imputed/estimated rather than directly observed prices it affects
  interpretability and potentially leakage.

## 5. Currency / regime structure (verified)

| Period | Currency present | Food cells |
|--------|------------------|-----------|
| 2010–2018 | USD only | ~3,100 (thin, annual) |
| 2019 | ZWL only | 94 |
| 2020–2022 | ZWL (a few USD in 2021) | ~11,200 |
| 2023 | mixed, ZWL-dominant | ~3,290 |
| 2024–2026 | USD-dominant, some ZWL | ~1,800 |

**Implication:** a single pooled nominal-price series mixes currencies with
incompatible scales. Any returns/target must be computed **within currency**, or on
`usdprice`, and the two targets reported separately. See Phase 2.

## 6. Coverage / reporting irregularity

- Reporting intensity is highly uneven: 2020–2023 account for ~**76%** of all food
  cells, while 2019 has 94. This is a **reporting artefact**, not a market signal.
- Only **37.1%** of monthly cells are followed by an observation in the next month
  (needed for a next-month label). Median series length is **4 months**.
- 336 markets appear in the price file but the market reference lists 486 — coverage
  is a subset; **a missing price is more likely a monitoring gap than low stress**
  (already acknowledged in the dissertation's limitations — keep it).

## 7. Geographic consistency

- `wfp_markets_zwe.csv` gives a market→(admin1, admin2, lat, lon) crosswalk for all
  336 price markets. 8 markets lack a district.
- geoBoundaries has 10 admin-1 and **91 admin-2** polygons. WFP `admin2` names (81)
  are a **subset** of the 91 polygons and use some different spellings / urban labels
  (e.g. "Marondera Urban", "Bulawayo", "Harare"). **Name-based joins will be lossy**;
  a coordinate-based point-in-polygon join is more defensible, with name matching as
  a cross-check. The HAPI file's P-codes can seed the crosswalk.
- **Spatial uncertainty is real** and must be reported: district assignment via
  coordinates + 2020 boundaries, and district rainfall applies one value to all
  markets in a district.

## 8. Potential data leakage risks (to be prevented in Phase 3)

1. **Target leakage via `usdprice`/`price` at t+1** — the label is derived from the
   future price; it must never be a predictor.
2. **Rolling/peer statistics** must be computed only from months ≤ t.
3. **Standardisation** of returns (mean/std) must use **trailing** windows or the
   training period only — not the whole sample.
4. **Rainfall anomalies** must use a baseline (long-term average) that would have been
   available at t (e.g. prior years only), not the full record including the future.
5. **Random splitting** would leak future months into training — must use chronological
   splits only.
6. **`priceflag=aggregate`** rows may embed cross-market/month information → confirm
   definition; if imputed from later data, restrict or flag.

## 9. Error/assumption log established in Phase 1

| ID | Item | Status |
|----|------|--------|
| E1 | `DataDetails.xls` unrelated to project | Confirmed; exclude |
| E2 | HAPI rainfall is admin-1 only | Confirmed; use `yr.nc` instead |
| E3 | Dissertation bibliography empty | Confirmed; must be built from scratch |
| E4 | No pipeline/parquet/model artefacts exist | Confirmed; all Ch3–5 implementation claims unsupported |
| E5 | `priceflag=aggregate` semantics | Open — must confirm |
| E6 | `usdprice` conversion basis | Open — must confirm |
| E7 | `usdprice` min 0.000015 | Open — inspect rows |
| E8 | WFP licence text | Open — confirm from HDX |
| E9 | CHIRPS global attr "convective precipitation rate" vs mm/month | Open — metadata inconsistency noted |

## 10. Overall quality verdict

The **price data are clean in structure** (no duplicates, no missing key fields) but
**heterogeneous in currency and sparsely and unevenly reported in time**. The
**rainfall situation is better than the dissertation implies** because `yr.nc` gives
genuine district-level CHIRPS, but the supplied HAPI rainfall file cannot. The main
quality threats are (i) currency non-comparability, (ii) short, uneven series, and
(iii) ambiguity in `priceflag`/`usdprice`. These are manageable but must shape the
target definition (Phase 2) and be disclosed prominently.
