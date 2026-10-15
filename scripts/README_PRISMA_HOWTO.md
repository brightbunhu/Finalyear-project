# README — Where to search and how to download the data for a real PRISMA

A hands-on, click-by-click guide. Follow it top to bottom; at the end you will have a
folder of real exported records that can be turned into the PRISMA flow. Nothing here
is estimated — every number comes from a file you downloaded.

---

## 0. Set up folders (once)

Create this structure in the project:

```
data/literature/
  raw/            <- exports land here, one file per database+stream
  dedup/          <- merged + de-duplicated library goes here
  screen/         <- your screening sheet(s)
  logs/           <- search_log.csv + screenshots of result counts
```

Put the search strings you will reuse in `logs/queries.txt`:

```
S1  "food price" AND ("machine learning" OR xgboost OR "random forest")
S2  "food price" AND (forecast OR prediction OR "early warning")
S3  "food price" AND (Zimbabwe OR "Southern Africa")
S4  ("food price" OR "food security") AND ("machine learning" OR "deep learning") AND (predict OR forecast OR crisis)
S5  ("price volatility" OR "price anomaly" OR "price stress") AND (food OR commodity) AND (machine learning OR prediction OR forecast)
S6  ("food price" OR "maize price" OR "market price") AND (rainfall OR drought OR climate) AND (Africa OR Zimbabwe)
```

---

## 1. OpenAlex (free, exportable, has a count)

1. Go to <https://openalex.org/>.
2. Paste a string from `queries.txt` into the search box (or use
   <https://openalex.org/works?filter=title_and_abstract.search:S1...>).
3. The page shows **"N works"** — write that number in `logs/search_log.csv`
   (column `identified_hits`).
4. To download: scroll to the bottom → **Download** → choose **CSV** (or use the API
   link shown). Save as `raw/openalex_S1.csv`.
   - Note: the web export may cap at a few thousand rows — record how many you actually
     got in the `retrieved` column.
5. Repeat for S1–S6.

## 2. Semantic Scholar (free, exports BibTeX)

1. Go to <https://www.semanticscholar.org/search?q=...> with a string.
2. Record the **"N results"** count.
3. Tick the results → **Export → BibTeX** (or "All" if offered). Save
   `raw/semanticscholar_Sx.bib`.
4. Repeat for each stream.

## 3. Google Scholar (needs a helper to export)

Google Scholar has no bulk export button, so use the free **Publish or Perish** app.

1. Download Publish or Perish: <https://harzing.com/resources/publish-or-perish>.
2. Choose **Google Scholar**, paste a string, set "Results" to e.g. 200 (it caps).
3. Note the **"About N results"** that Scholar shows in a browser and record it.
4. In PoP: **Save → RIS / CSV / EndNote**. Save `raw/scholar_Sx.csv`.
5. Repeat. (Scholar is good for recall; its export is capped, so note the cap.)

## 4. DOAJ (open-access articles, exports CSV/RIS)

1. Go to <https://doaj.org/search/journals> → switch to **Articles**.
2. Paste a string, search. Record the hit count.
3. **Export → CSV** (max 1000 per export; if more, page through and export again).
   Save `raw/doaj_Sx.csv`.

## 5. PubMed (health/climate angle, exports .nbib)

1. Go to <https://pubmed.ncbi.nlm.nih.gov/>.
2. Paste a string. Record the count.
3. **Save → Citation manager** → creates `pubmed_Sx.nbib`. Save under `raw/`.

## 6. Scopus / Web of Science (only if your library gives access)

1. Log in through your university library.
2. Advanced search → paste the string → search. Record the count.
3. **Export → RIS / CSV / BibTeX** (may need to select "Records 1–N" or export in
   batches of 2000). Save `raw/scopus_Sx.ris`.
4. Same for Web of Science → **Export → Other File Formats → RIS / Tab-delimited**.

> If you have no institutional access, simply skip these and say so. Do **not** guess
> their counts.

---

## 7. Save the search log (this is the Identification box)

`logs/search_log.csv` — one row per database × stream:

```csv
stream,database,date,query,identified_hits,retrieved
S1,OpenAlex,2026-10-20,"""food price"" AND (""machine learning"" OR xgboost OR ""random forest"")",191,191
S1,Google Scholar,2026-10-20,"""food price"" AND ...",1820,200
S2,OpenAlex,2026-10-20,"""food price"" AND (forecast OR prediction OR ""early warning"")",1144,1144
```

Also drop a **screenshot** of each result count into `logs/` — cheap evidence for a viva.

**Identified (PRISMA)** = sum of `identified_hits`.

---

## 8. Merge and de-duplicate (the Duplicates + Unique boxes)

Install **Zotero** (<https://www.zotero.org/>; free).

1. In Zotero: **File → Import** → import every file in `raw/` (.csv/.ris/.bib/.nbib).
   Put them in one collection, e.g. "Lit search".
2. Optional: **Tools → Manage duplicates** / select all and use "Duplicate Items".
3. Export the de-duplicated library: right-click collection → **Export Collection →
   CSV**. Save `dedup/library.csv`.
4. Count rows:
   - **Duplicates removed** = Identified − (rows in `library.csv`).
   - **Unique records screened** = rows in `library.csv`.

(Excel alternative: import all CSVs, sort by DOI then Title, use *Data → Remove
Duplicates*.)

---

## 9. Screen title/abstract (the Screening boxes)

Install **Rayyan** (<https://rayyan.ai/>; free) or use your sheet.

1. Import `dedup/library.csv` into a Rayyan review.
2. Apply the rules for each record:
   - **topic** = food/commodity *prices* or food security? (yes/no)
   - **method** = model / forecast / prediction / ML? (yes/no)
   - **language** = English? **type** = article / review / conference paper?
3. Mark **Include / Exclude**, and for each exclude pick a reason.

Copy into `screen/screen.csv`:

```csv
id,title,year,type,source,topic,method,english,refereed,include,exclude_reason,notes
```

Counts:
- **Excluded at screening** = (no topic) + (no method) + (non-English) + (untitled).
- **Passed screening** = Unique screened − Excluded at screening.
- **Full-text assessed** = Passed screening.
- **Excluded at eligibility** = passed screening but not refereed article/review/conf.
- **Candidate pool** = Passed screening − Excluded at eligibility.
- **Included** = the works you actually cite (aim ≥ 20 refereed). Keep **grey reports**
  (WFP, FEWS NET, World Bank, IMF, ZimLAC) in a separate count.

---

## 10. Fill the PRISMA flow

Open `reports/revision/prisma_flow.md` and replace each number with the value you
logged:

```
Identified -> Duplicates removed -> Unique screened -> Passed screening ->
Candidate pool -> Included (+ grey, separate)
```

Every number must trace to `logs/search_log.csv` or `screen/screen.csv`.

---

## Quick reference — free tools

| Need | Tool | Link |
|------|------|------|
| Reference manager + dedupe | Zotero | https://www.zotero.org/ |
| Screening | Rayyan | https://rayyan.ai/ |
| Google Scholar export | Publish or Perish | https://harzing.com/resources/publish-or-perish |
| Open search + export | OpenAlex | https://openalex.org/ |
| Free OA articles | DOAJ | https://doaj.org/ |
| Health/climate | PubMed | https://pubmed.ncbi.nlm.nih.gov/ |
| Spreadsheets | Google Sheets / Excel | — |

---

## Minimal version (if you are short on time)

You do **not** need six databases. A defensible minimum:

1. **OpenAlex** — run all 6 strings, export CSV, record counts.
2. **Google Scholar via Publish or Perish** — same strings, export CSV.
3. De-duplicate in Zotero or Excel.
4. Screen in one sheet.
5. Fill the flow.

Two databases + a documented dedupe + a written screening rule = a real, checkable
PRISMA. That is enough. Just keep the exports and the log — those are your evidence.
