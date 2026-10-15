# README — Systematic search (PRISMA), API key, and human borderline calls

> **Update (2026-10-15):** the PRISMA flow is now built from the author's **downloaded
> exports** (`data/literature/raw/`) by `scripts/prisma_ingest.py`, covering three
> databases — **OpenAlex, Semantic Scholar and PubMed**. That script supersedes the
> live-API approach below and produces `reports/revision/prisma_flow.md`,
> `prisma_records.csv`, `prisma_search_log.csv`, plus `data/literature/dedup/library.csv`
> and `data/literature/screen/screening_sheet.csv`.
>
> `scripts/openalex_enrich.py` re-queries the OpenAlex REST API **by DOI** to recover the
> `type` and abstract that the web export omits (→
> `data/literature/raw/openalex_enriched.csv`), and `prisma_ingest.py` merges it before
> screening. It reads the key from the `OPENALEX_API_KEY` environment variable or from
> `scripts/.openalex_key` (never written to output). The API-key and borderline sections
> below apply only to the older `phase2_prisma*.py` scripts.

This folder reproduces the Chapter 2 systematic search and PRISMA flow. There are two
things **you (the human) need to supply**: an OpenAlex API key (optional but
recommended), and the borderline screening decisions in `prisma_borderline.csv`.

---

## 1. The OpenAlex API key (what I want from you)

### Why
The live search in `scripts/phase2_prisma.py` queries the **OpenAlex** REST API. Without
a key it works, but it counts against a **shared free daily budget** ("Insufficient
budget — this request has no API key") and it cannot use cursor paging. A free key:
- removes the shared-budget limit (10 requests/second, 100,000/day for you);
- lets the script use cursor paging (no `page × per_page ≤ 10 000` cap).

You do **not** need a paying account. A free key is issued in about a minute.

### How to get it
1. Go to <https://openalex.org/> and click **Sign in** (or
   <https://openalex.org/settings/api>).
2. Create a free account (email + a mailto), open **Settings → API key**, and copy the
   key (a long string starting with `oa_`… or a plain token).
3. Do **not** email it in plain text if you can avoid it — instead put it in the file
   below on your machine.

### How to give it to the scripts
Either set an environment variable:

```powershell
$env:OPENALEX_API_KEY = "your-key-here"
```

or create the file `scripts/.openalex_key` containing only the key on one line:

```
your-key-here
```

`phase2_prisma.py` reads the environment variable first, then falls back to
`scripts/.openalex_key`. **Do not commit `scripts/.openalex_key`** to any repository
(it is a secret).

### Re-run the live search once the key is set
```powershell
python scripts\phase2_prisma.py
python scripts\phase2_prisma_report.py
python scripts\phase2_prisma_borderline.py
```

The key only affects *how* the search runs; the screening rules and report are
unchanged. If the shared budget is exhausted and you have no key, you can still
regenerate the flow offline (see §3) from the cached records already in this folder.

---

## 2. Human borderline calls (what I want from you)

Automated screening can wrongly drop (false negative) or wrongly keep a record. The
records that could actually change the review are exported to:

```
reports/revision/prisma_borderline.csv      (192 rows)
```

Two groups, tagged in the `borderline_reason` column:

| Group | n | Meaning | Your call |
|-------|---|---------|-----------|
| `P1 refereed_food_title_excluded` | 67 | A **refereed article with a food/price term in its title** that the keyword screen still excluded — the most likely **false negatives** | Include / Exclude / Unsure |
| `P2 grey_eligible_food_title` | 125 | A **non-refereed record** (preprint / report / book chapter / dissertation) that passed the topic+method+English screen and has a food/price term in its title — a plausible **grey-literature include** | Include (as grey) / Exclude |

### How to make the calls
1. Open `reports/revision/prisma_borderline.csv` in Excel (or any spreadsheet).
2. For each row, read `title` (+ `year`, `type`, `venue`) and fill two columns:
   - `human_decision` — one of `Include`, `Exclude`, `Unsure`.
   - `human_notes` — a short reason (e.g., "off-topic", "not food prices", "keep as grey").
3. Save the file. Tell me when it is done and I will:
   - fold your decisions back into the PRISMA flow (`prisma_flow.md`),
   - update the "Studies included" count and add an "excluded with reasons" breakdown,
   - add any newly included works to `references.md` with the 5Cs extraction.

### What to look for
- **P1**: does the article predict/forecast food or commodity *prices*, or use a
  price-driver model? If it names a model/forecast in the abstract but not in the
  title/abstract text the keyword rule missed, mark `Include`.
- **P2**: is it a genuine primary study or authoritative report on food price stress /
  drivers (or methods used here)? If yes, `Include` as grey literature; if it is a
  working paper superseded by a journal article, prefer the journal version.

### Context numbers (for reference, not in the worklist)
In the full retrieval: 232 eligible preprints, 214 eligible book chapters, 64 eligible
reports. These are **not** all borderline; they are only exported when a food/price
term is in the title (group P2).

---

## 3. Regenerate everything offline (no network)

If you only want to rebuild the flow / worklist from the already-retrieved records:

```powershell
python scripts\phase2_prisma_report.py       # rebuilds prisma_flow.md
python scripts\phase2_prisma_borderline.py   # rebuilds prisma_borderline.csv
```

These read `reports/revision/prisma_records.csv` + `prisma_search_log.csv` and make **no
API calls**.

---

## Files

| File | Role |
|------|------|
| `prisma_ingest.py` | **Preferred:** build the flow from downloaded exports (3 databases) |
| `openalex_enrich.py` | Recover OpenAlex `type`/abstract by DOI (needs key) |
| `phase2_prisma.py` *(legacy)* | Live OpenAlex search → records + search log (needs network / key) |
| `phase2_prisma_report.py` *(legacy)* | Offline: builds `prisma_flow.md` from cached records |
| `phase2_prisma_borderline.py` *(legacy)* | Offline: builds the human `prisma_borderline.csv` worklist |
| `.openalex_key` | One-line API key (secret; do not commit) |
| `../reports/revision/prisma_flow.md` | The PRISMA flow (goes in Appendix A) |
| `../reports/revision/prisma_records.csv` | Unique screened records + flags (from `prisma_ingest.py`) |
| `../reports/revision/prisma_search_log.csv` | Per-query hit counts and retrieval |
| `../reports/revision/prisma_borderline.csv` | *(legacy)* borderline worklist from `phase2_prisma_borderline.py` |

---

## Summary of the two asks

1. **API key** → drop it in `scripts/.openalex_key` (or `$env:OPENALEX_API_KEY`) so the
   live search can re-run without the shared-budget limit.
2. **Borderline calls** → fill `human_decision` + `human_notes` in
   `reports/revision/prisma_borderline.csv` (192 rows) and tell me; I will finalise the
   PRISMA flow and the included-study list.
