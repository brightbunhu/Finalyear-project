# README (DIY) — Complete the systematic search & PRISMA on your own

This is a self-service guide so you can run and finish the Chapter 2 systematic search
**by yourself**, with no API key and no help from me. Everything here uses free, public
tools.

One rule runs through all of it: **the numbers must be real.** Every count in the PRISMA
flow must be something a database or tool actually returned on the date you ran it. If
you cannot get a number, write "not recorded" — never guess. (This is what makes the
method defensible in a viva.)

There are two paths. Pick one.

---

## Path A — Run the scripts without a key (fastest, still real)

The scripts already work without an API key:

```powershell
python scripts\phase2_prisma.py            # live search (may hit the shared budget)
python scripts\phase2_prisma_report.py     # rebuild flow from whatever was retrieved
python scripts\phase2_prisma_borderline.py # rebuild your decision list
```

If `phase2_prisma.py` prints `429 ... Insufficient budget`, the shared free pool is
exhausted for the day. Wait 24 hours, or get a free key in ~1 minute
(<https://openalex.org/settings/api>) and drop it in `scripts/.openalex_key`. You can
always rebuild the flow offline from the cached `prisma_records.csv`.

---

## Path B — Do it completely manually (no code, no key)

Use this if you cannot get a key or want to show a classic database search.

### B1. Databases (all free to search)
| Database | URL | Notes |
|----------|-----|-------|
| OpenAlex | https://openalex.org/ | free web search, shows a result count |
| Google Scholar | https://scholar.google.com/ | shows "About X results" |
| Semantic Scholar | https://www.semanticscholar.org/ | free |
| DOAJ | https://doaj.org/ | open-access articles |
| PubMed | https://pubmed.ncbi.nlm.nih.gov/ | health/climate angle |
| Scopus / Web of Science | institutional login | only if your library gives access |

### B2. Search strings (paste these; copy the result count for each)
Run each string in each database you use and record the count it reports.

| # | String |
|---|--------|
| S1 | `"food price" AND ("machine learning" OR xgboost OR "random forest")` |
| S2 | `"food price" AND (forecast OR prediction OR "early warning")` |
| S3 | `"food price" AND (Zimbabwe OR "Southern Africa")` |
| S4 | `("food price" OR "food security") AND ("machine learning" OR "deep learning") AND (predict OR forecast OR crisis)` |
| S5 | `("price volatility" OR "price anomaly" OR "price stress") AND (food OR commodity) AND (machine learning OR prediction OR forecast)` |
| S6 | `("food price" OR "maize price" OR "market price") AND (rainfall OR drought OR climate) AND (Africa OR Zimbabwe)` |

### B3. Record your search log (the "Identification" box)
Fill a sheet `prisma_search_log.csv` like this (one row per database × string):

```csv
stream,database,date,query,identified_hits,retrieved
S1,Google Scholar,2026-10-20,"""food price"" AND ...",1820,50
S1,OpenAlex,2026-10-20,"""food price"" AND ...",191,191
```

- `identified_hits` = the number the database shows for that string.
- `retrieved` = how many you actually saved/exported (often capped; note the cap).

### B4. Export and de-duplicate (the "Screening" boxes)
1. Export the results you want to keep as `.csv` / `.ris` / `.bib` (most sites have an
   export button; if not, save the titles+DOI into a spreadsheet).
2. Load everything into **Zotero** (free) → select all → right-click → *Duplicate Items*,
   or use **Excel**: sort by DOI/Title and remove exact repeats.
3. Count:
   - **Identified** = sum of `identified_hits` across your log.
   - **Duplicates removed** = Identified − (unique records after dedupe).
   - **Unique screened** = the number left after dedupe.

### B5. Screen title/abstract
1. Open your unique list in a sheet (or **Rayyan**, free: https://rayyan.ai/).
2. For each record apply the rules:
   - about food/commodity **prices / food security**? (topic)
   - uses a **model / forecast / prediction / ML**? (method)
   - in **English**? refereed article/review/conference paper? (type)
3. Mark Include / Exclude and, if excluded, the reason (no topic / no method /
   non-English / not refereed).
4. Count:
   - **Excluded at screening** = (no topic) + (no method) + (non-English) + (untitled).
   - **Passed screening** = Unique screened − Excluded.
   - **Full-text assessed** = Passed screening.
   - **Excluded at eligibility** = passed screening but not a refereed article/review/conf.
   - **Candidate pool** = passed screening − excluded at eligibility.

### B6. Included studies
- **Included** = the works you actually cite and analyse (aim ≥ 20 refereed).
- Keep **grey reports** (WFP, FEWS NET, World Bank, IMF, ZimLAC…) counted separately.
- Record each included source in `references.md` with the 5Cs.

### B7. Fill the flow
Open `reports/revision/prisma_flow.md` and replace each number with **your logged
values**. The five boxes are:
```
Identified → Duplicates removed → Unique screened → Passed screening →
Candidate pool → Included (+ grey, separate)
```
Every number must match a row in `prisma_search_log.csv` or your screening sheet.

---

## Blank templates

`prisma_search_log.csv`
```csv
stream,database,date,query,identified_hits,retrieved
```

Screen sheet (`my_screen.csv`)
```csv
id,title,year,type,source,include,exclude_reason,notes
```

---

## Free tools worth installing
- **Zotero** — reference manager + duplicate detection: https://www.zotero.org/
- **Rayyan** — PRISMA-style screening: https://rayyan.ai/
- **Google Sheets / Excel** — search log and screen sheet
- **OpenAlex / Google Scholar** — the searches themselves

---

## Self-check before you submit
- [ ] Every identified count came from a real search, dated.
- [ ] Duplicates computed by an actual dedupe step (Zotero/Excel), not estimated.
- [ ] Screening rules written down (topic + method + language + type).
- [ ] ≥ 20 refereed articles included; grey literature separated.
- [ ] Each included source has a full reference and a 5Cs entry.
- [ ] No number in `prisma_flow.md` that you cannot point to in your log/sheet.

---

## What I can do for you afterwards
When your `prisma_search_log.csv` and screen sheet are filled, I can:
- format them into `prisma_flow.md`,
- update the included-study list and `references.md`,
- re-compile `Chapters_1-5_revised.docx`.

But the counts have to be yours and real — I cannot make them up for you.
