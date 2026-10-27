# README — Download the data for a real PRISMA (step by step)

Follow these steps exactly. At the end, this folder will contain everything needed to
build the PRISMA flow. Every number comes from a file you downloaded — nothing is
estimated.

## What you will end up with
```
data/literature/raw/openalex_S1.csv ... openalex_S6.csv
data/literature/raw/scholar_S1.csv  ... scholar_S6.csv
data/literature/logs/search_log.csv
```
12 export files + 1 log. That is the whole requirement.

Folders already created for you:
```
data/literature/raw/     -> put download files here
data/literature/dedup/   -> merged + de-duplicated library goes here
data/literature/screen/  -> screening sheet goes here
data/literature/logs/    -> search_log.csv + screenshots of counts
```

## The search strings (paste these)
```
S1  "food price" AND ("machine learning" OR xgboost OR "random forest")
S2  "food price" AND (forecast OR prediction OR "early warning")
S3  "food price" AND (Zimbabwe OR "Southern Africa")
S4  ("food price" OR "food security") AND ("machine learning" OR "deep learning") AND (predict OR forecast OR crisis)
S5  ("price volatility" OR "price anomaly" OR "price stress") AND (food OR commodity) AND (machine learning OR prediction OR forecast)
S6  ("food price" OR "maize price" OR "market price") AND (rainfall OR drought OR climate) AND (Africa OR Zimbabwe)
```

---

## Step 1 — OpenAlex (6 files, ~10 minutes)

1. Open <https://openalex.org/> in a browser.
2. Paste stream **S1** into the search box and press Enter.
3. Read the **"N works"** count shown above the results (top-left).
4. Write that number into `logs/search_log.csv` (column `identified_hits`).
5. Scroll to the **bottom of the results list** and click **Download**.
6. Choose **CSV**.
7. Save the file as `raw/openalex_S1.csv`.
8. Repeat steps 2–7 for **S2, S3, S4, S5, S6**, saving as
   `raw/openalex_S2.csv` … `raw/openalex_S6.csv`.

Tip: the web export may cap at a few thousand rows. If so, note how many rows you
actually received in the `retrieved` column.

---

## Step 2 — Google Scholar, via Publish or Perish (6 files)

Google Scholar itself has no download button, so use the free Publish or Perish app.

1. Download **Publish or Perish**: <https://harzing.com/resources/publish-or-perish>.
2. Install and open it.
3. Go to the **Google Scholar** tab.
4. Paste stream **S1**, set the **Results** field to `200`, and click **Lookup**.
5. Record the number of results in `logs/search_log.csv`.
6. Click **Save** → choose **CSV**.
7. Save as `raw/scholar_S1.csv`.
8. Repeat steps 4–7 for **S2 … S6**, saving as `raw/scholar_S2.csv` … `scholar_S6.csv`.

---

## Step 3 — Create the search log

Create `data/literature/logs/search_log.csv` with this header:

```csv
stream,database,date,query,identified_hits,retrieved
```

Then add one row per database × stream. Example:

```csv
stream,database,date,query,identified_hits,retrieved
S1,OpenAlex,2026-10-20,"""food price"" AND (""machine learning"" OR xgboost OR ""random forest"")",191,191
S1,GoogleScholar,2026-10-20,"""food price"" AND (""machine learning"" OR xgboost OR ""random forest"")",1820,200
S2,OpenAlex,2026-10-20,"""food price"" AND (forecast OR prediction OR ""early warning"")",1144,1144
```

- `identified_hits` = the number the website showed for that search.
- `retrieved` = the number of rows in the file you saved.

---

## Step 4 — Optional but recommended: evidence of the counts

Take a screenshot of each result count (OpenAlex and Publish or Perish) and drop the
images in `logs/`. This lets anyone verify the numbers at a viva.

---

## Step 5 — Hand it over

When the 12 files and `search_log.csv` are in place, tell me. I will write an ingest
script that:

1. reads all 12 export files,
2. de-duplicates them into `dedup/library.csv`,
3. creates a screening sheet in `screen/`,
4. fills `reports/revision/prisma_flow.md` with your real numbers.

---

## If you only have time for the minimum

Two databases are enough for a real, checkable PRISMA:

1. **OpenAlex** — all 6 strings, export CSV.
2. **Google Scholar (Publish or Perish)** — all 6 strings, export CSV.
3. Log the counts.
4. Screenshot the counts.

Then hand over. Documented searches + a written screening rule + the exports = a
defensible PRISMA. Do **not** invent any count; write "not recorded" if you cannot get
one.
