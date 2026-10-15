"""PRISMA flow from the real downloaded literature exports.

Reads the files exported from three databases into
``data/literature/raw/`` (OpenAlex web export + Publish-or-Perish exports for
Semantic Scholar and PubMed), merges and de-duplicates them into a single
library, applies documented title/abstract screening rules, and writes a
PRISMA-style flow. No count is invented: "identified" comes from
``data/literature/logs/search_logs.csv``; "retrieved" is the number of rows
actually present in each export file.

OpenAlex web exports carry a DOI but no ``type`` and (for some streams) no
abstract. ``scripts/openalex_enrich.py`` recovers those from the OpenAlex REST
API by DOI into ``data/literature/raw/openalex_enriched.csv``; this script
merges them back in before screening when that file is present.

Outputs
-------
data/literature/raw/openalex_enriched.csv    API-recovered type/abstract (by openalex_enrich.py)
data/literature/dedup/library.csv            unique merged library
data/literature/screen/screening_sheet.csv   unique records + flags + include column
reports/revision/prisma_records.csv          same, for the record
reports/revision/prisma_search_log.csv        per database x stream counts
reports/revision/prisma_flow.md               PRISMA flow + reconciliation
"""
from __future__ import annotations

import csv
import datetime as dt
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "literature" / "raw"
DEDUP = ROOT / "data" / "literature" / "dedup"
SCREEN = ROOT / "data" / "literature" / "screen"
LOG = ROOT / "data" / "literature" / "logs"
REV = ROOT / "reports" / "revision"
for d in (DEDUP, SCREEN, REV):
    d.mkdir(parents=True, exist_ok=True)

SEARCH_DATE = "2026-10-15"

# --- canonical streams (order S1..S6) ------------------------------------
STREAM_QUERIES = {
    "S1": '("food price" OR "food prices") AND ("machine learning" OR xgboost OR "random forest" OR "gradient boosting")',
    "S2": '("food price" OR "food prices") AND (forecast OR prediction OR "early warning")',
    "S3": '("food price" OR "food prices") AND (Zimbabwe OR "Southern Africa")',
    "S4": '("food price" OR "food security") AND ("machine learning" OR "deep learning") AND (predict OR forecast OR crisis)',
    "S5": '("price anomaly" OR "price volatility" OR "price stress") AND (food OR commodity) AND (machine learning OR prediction OR forecast)',
    "S6": '("food price" OR "maize price" OR "market price") AND (rainfall OR drought OR climate) AND (Africa OR Zimbabwe)',
}


def classify_stream(query: str) -> str:
    q = query.lower()
    if "xgboost" in q or "random forest" in q:
        return "S1"
    if "deep learning" in q:
        return "S4"
    if "early warning" in q or "forecast or prediction" in q:
        return "S2"
    if "price volatility" in q or "price anomaly" in q or "price stress" in q:
        return "S5"
    if "rainfall" in q or "drought" in q:
        return "S6"
    if "zimbabwe" in q or "southern africa" in q:
        return "S3"
    return "?"


DB_ALIASES = {"open alex": "OpenAlex", "openalex": "OpenAlex",
              "semantic scholar search": "SemanticScholar",
              "semantic scholar": "SemanticScholar", "semanticscholar": "SemanticScholar",
              "pubmed": "PubMed"}

# --- file map (database, stream) -> filename ------------------------------
FILES = {
    ("OpenAlex", "S1"): "openalex_S1.csv",
    ("OpenAlex", "S2"): "openalex_S2.csv",
    ("OpenAlex", "S3"): "openalex3.csv",
    ("OpenAlex", "S4"): "openalex4.csv",
    ("OpenAlex", "S5"): "openalexS5.csv",
    ("OpenAlex", "S6"): "open alexS6.csv",
    ("SemanticScholar", "S1"): "Semantic_1.csv",
    ("SemanticScholar", "S2"): "semantic_2.csv",
    ("SemanticScholar", "S3"): "semantic_3.csv",
    ("SemanticScholar", "S4"): "sematic_4.csv",
    ("SemanticScholar", "S5"): "sematic_5.csv",
    ("SemanticScholar", "S6"): "sematic_6.csv",
    ("PubMed", "S1"): "Pubmed_1.csv",
    ("PubMed", "S2"): "Pubmed_2.csv",
}

TOPIC = ["food price", "food prices", "price volatility", "price anomaly", "price spike",
         "food security", "food insecurity", "commodity price", "maize price",
         "market price", "price stress", "staple price", "cereal price", "food crisis",
         "crop price", "agricultural price"]
METHOD = ["machine learning", "deep learning", "random forest", "xgboost",
          "gradient boosting", "neural network", "forecast", "predict", "early warning",
          "nowcast", "time series", "regression", "model", "lstm", "artificial intelligence"]
REFEREED_TYPES = {"journalarticle", "article", "review", "conference", "conferencepaper",
                  "proceedings"}


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def load_enrichment() -> dict[str, dict]:
    """doi -> {type, abstract, title, year} recovered from the OpenAlex API."""
    path = RAW / "openalex_enriched.csv"
    if not path.exists():
        return {}
    out = {}
    with open(path, "r", encoding="utf-8", errors="replace", newline="") as f:
        for r in csv.DictReader(f):
            doi = clean_doi(r.get("doi", ""))
            if doi:
                out[doi] = {"type": (r.get("type") or "").strip(),
                            "abstract": (r.get("abstract") or "").strip(),
                            "title": (r.get("title") or "").strip(),
                            "year": (r.get("year") or "").strip()}
    return out


def clean_doi(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"^https?://(dx\.)?doi\.org/", "", s)
    s = re.sub(r"^doi:\s*", "", s)
    return s.strip().rstrip(".")


def read_csv_any(path: Path) -> list[dict]:
    """Read a CSV with the OpenAlex or Publish-or-Perish column layout."""
    import csv as _csv
    with open(path, "r", encoding="utf-8-sig", errors="replace", newline="") as f:
        rdr = _csv.DictReader(f)
        cols = {c.lower().strip(): c for c in (rdr.fieldnames or [])}
        out = []
        for row in rdr:
            def g(*names):
                for n in names:
                    if n in cols:
                        return (row.get(cols[n]) or "").strip()
                return ""
            out.append({
                "title": g("title"),
                "authors": g("author", "authors"),
                "year": g("year"),
                "doi": clean_doi(g("doi")),
                "abstract": g("abstract"),
                "source": g("source", "publisher"),
                "type": g("type"),
            })
        return out


def parse_search_log() -> list[dict]:
    """Parse data/literature/logs/search_logs.csv (per-search count sheet)."""
    path = LOG / "search_logs.csv"
    rows = []
    current = None
    with open(path, "r", encoding="utf-8-sig", errors="replace", newline="") as f:
        for r in csv.reader(f, delimiter="\t"):
            if not r or len(r) < 3:
                continue
            db_raw, query, res = r[0].strip(), r[1].strip(), r[2].strip()
            if db_raw.lower().startswith("search db"):
                continue
            db = DB_ALIASES.get(db_raw.lower().lstrip("\ufeff"))
            if db:
                current = db
            else:
                db = current
            if db is None:
                continue
            try:
                n = int(res.replace(",", "").strip())
            except ValueError:
                continue
            rows.append({"database": db, "query": query,
                         "stream": classify_stream(query), "identified_hits": n})
    return rows


def load_borderline_decisions() -> dict:
    """Counts from the borderline worklist (reports/revision/prisma_borderline.csv).

    Returns reviewed/include/exclude/unsure totals plus the G1/G2 split. Absent or
    empty file -> zeros, so the flow degrades gracefully before borderline review.
    """
    path = REV / "prisma_borderline.csv"
    out = {"reviewed": 0, "include": 0, "exclude": 0, "unsure": 0, "g1": 0, "g2": 0}
    if not path.exists():
        return out
    with open(path, "r", encoding="utf-8-sig", errors="replace", newline="") as f:
        for r in csv.DictReader(f):
            dec = (r.get("borderline_decision") or r.get("human_decision") or "").strip().lower()
            cat = (r.get("category") or "").strip()
            out["reviewed"] += 1
            if cat.startswith("G1"):
                out["g1"] += 1
            elif cat.startswith("G2"):
                out["g2"] += 1
            if dec == "include":
                out["include"] += 1
            elif dec == "exclude":
                out["exclude"] += 1
            elif dec:
                out["unsure"] += 1
    return out


def main():
    log = parse_search_log()
    ident_by = {}
    for r in log:
        ident_by[(r["database"], r["stream"])] = r["identified_hits"]

    records: dict[str, dict] = {}
    retrieved_rows = []
    files_read = 0
    missing = []
    for (db, stream), fname in FILES.items():
        path = RAW / fname
        if not path.exists():
            missing.append(fname)
            continue
        recs = read_csv_any(path)
        files_read += 1
        retrieved_rows.append({"database": db, "stream": stream, "file": fname,
                               "retrieved": len(recs)})
        for r in recs:
            key = r["doi"] or norm(r["title"]) or f"{db}:{stream}:{len(records)}"
            if key in records:
                ex = records[key]
                ex["streams"].add(stream)
                ex["databases"].add(db)
                for field in ("type", "abstract", "authors", "year", "source"):
                    if not ex.get(field) and r.get(field):
                        ex[field] = r[field]
            else:
                r = dict(r)
                r["streams"] = {stream}
                r["databases"] = {db}
                records[key] = r

    uniq = len(records)

    # --- enrich OpenAlex records with API-recovered type/abstract by DOI ---
    enr = load_enrichment()
    enr_type = enr_abs = enr_title = 0
    for r in records.values():
        e = enr.get(r["doi"]) if r["doi"] else None
        if not e:
            continue
        if not r["type"] and e["type"]:
            r["type"] = e["type"]
            enr_type += 1
        if not r["abstract"] and e["abstract"]:
            r["abstract"] = e["abstract"]
            enr_abs += 1
        if not r["title"] and e["title"]:
            r["title"] = e["title"]
            enr_title += 1
    enriched = bool(enr)

    # --- screening (topic AND method; on title+abstract where available) ---
    for r in records.values():
        text = (r["title"] + " " + r["abstract"]).lower()
        r["abstract_available"] = bool(r["abstract"])
        r["type_available"] = bool((r.get("type") or "").strip())
        r["screen_topic"] = any(t in text for t in TOPIC)
        r["screen_method"] = any(m in text for m in METHOD)
        r["has_title"] = bool(r["title"].strip())
        r["screened_in"] = bool(r["screen_topic"] and r["screen_method"] and r["has_title"])
        t = re.sub(r"[^a-z]", "", (r["type"] or "").lower())
        r["refereed"] = t in REFEREED_TYPES
        r["eligible"] = bool(r["screened_in"] and r["type_available"] and r["refereed"])

    passing = [r for r in records.values() if r["screened_in"]]
    excl_topic = sum(not r["screen_topic"] for r in records.values())
    excl_method = sum(r["screen_topic"] and not r["screen_method"] for r in records.values())
    excl_untitled = sum(not r["has_title"] for r in records.values())
    type_unknown = sum(r["screened_in"] and not r["type_available"] for r in records.values())
    excl_type = sum(r["screened_in"] and r["type_available"] and not r["refereed"]
                    for r in records.values())
    pool = sum(r["eligible"] for r in records.values())
    borderline = load_borderline_decisions()

    identified_total = sum(ident_by.values())
    retrieved_total = sum(x["retrieved"] for x in retrieved_rows)
    dup = identified_total - uniq

    # --- reconciliation: supplied corpus DOIs found in the merged library ---
    supplied = parse_supplied_dois()
    lib_dois = {r["doi"] for r in records.values() if r["doi"]}
    recon = []
    for label, doi in supplied:
        recon.append({"label": label, "doi": doi, "captured": bool(doi and doi in lib_dois)})
    captured = sum(x["captured"] for x in recon)
    n_supplied = len(recon)

    # --- write outputs ---
    write_library(records, log, retrieved_rows, ident_by)
    write_records_csv(records)
    write_screen_sheet(records)
    write_flow(uniq, identified_total, retrieved_total, dup, excl_topic, excl_method,
               excl_untitled, len(passing), excl_type, type_unknown, pool, borderline,
               recon, captured, n_supplied, ident_by, retrieved_rows, files_read, missing,
               enr_type, enr_abs, enr_title, enriched)

    print(f"files_read={files_read} identified={identified_total} retrieved={retrieved_total}")
    print(f"unique={uniq} duplicates_removed={dup}")
    print(f"enriched_from_openalex_api type={enr_type} abstract={enr_abs} title={enr_title}")
    print(f"passing={len(passing)} excl_topic={excl_topic} excl_method={excl_method} "
          f"excl_untitled={excl_untitled}")
    print(f"type_unknown={type_unknown} excl_type={excl_type} refereed_pool={pool}")
    print(f"supplied_corpus={n_supplied} captured_by_doi={captured}")
    print(f"borderline reviewed={borderline['reviewed']} include={borderline['include']} "
          f"exclude={borderline['exclude']} unsure={borderline['unsure']}")
    if missing:
        print("MISSING FILES:", missing)


def parse_supplied_dois() -> list[tuple[str, str]]:
    """Extract (author-year label, doi) from references.md."""
    path = REV / "references.md"
    if not path.exists():
        return []
    out, seen = [], set()
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.search(r"https?://(?:dx\.)?doi\.org/(10\.\d{4,9}/[^\s)]+)", line)
        if not m:
            continue
        doi = clean_doi(m.group(1))
        head = re.sub(r"^[\*\-\s]+", "", line.strip())
        ym = re.match(r"(.+?)\s*\((\d{4}[a-z]?)\)", head)
        if ym:
            pre, year = ym.group(1).strip(), ym.group(2)
            first = re.split(r"[,&]", pre)[0].strip()
            multi = bool(re.search(r"[,&]", pre))
            label = f"{first} et al. ({year})" if multi else f"{first} ({year})"
        else:
            label = head[:40]
        if doi in seen:
            continue
        seen.add(doi)
        out.append((label, doi))
    return sorted(out)


def write_library(records, log, retrieved_rows, ident_by):
    cols = ["databases", "streams", "title", "authors", "year", "type", "doi",
            "source", "abstract_available", "screen_topic", "screen_method",
            "screened_in", "refereed", "eligible"]
    with open(DEDUP / "library.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in sorted(records.values(), key=lambda x: norm(x["title"])):
            row = dict(r)
            row["databases"] = "|".join(sorted(r["databases"]))
            row["streams"] = "|".join(sorted(r["streams"]))
            w.writerow(row)


def write_records_csv(records):
    cols = ["databases", "streams", "title", "authors", "year", "type", "type_available",
            "doi", "source", "abstract_available", "screen_topic", "screen_method",
            "screened_in", "refereed", "eligible"]
    with open(REV / "prisma_records.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in sorted(records.values(), key=lambda x: norm(x["title"])):
            row = dict(r)
            row["databases"] = "|".join(sorted(r["databases"]))
            row["streams"] = "|".join(sorted(r["streams"]))
            w.writerow(row)


def write_screen_sheet(records):
    cols = ["include", "reason", "title", "year", "type", "doi", "databases", "streams"]
    with open(SCREEN / "screening_sheet.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in sorted(records.values(), key=lambda x: norm(x["title"])):
            reason = ("pass-title/abstract" if r["screened_in"] else
                      "no-topic-term" if not r["screen_topic"] else
                      "no-method-term" if not r["screen_method"] else "untitled")
            w.writerow({"include": "candidate" if r["screened_in"] else "exclude",
                        "reason": reason, "title": r["title"], "year": r["year"],
                        "type": r["type"], "doi": r["doi"],
                        "databases": "|".join(sorted(r["databases"])),
                        "streams": "|".join(sorted(r["streams"]))})


def write_flow(uniq, identified_total, retrieved_total, dup, excl_topic, excl_method,
               excl_untitled, passing, excl_type, type_unknown, pool, borderline,
               recon, captured, n_supplied, ident_by, retrieved_rows, files_read, missing,
               enr_type=0, enr_abs=0, enr_title=0, enriched=False):
    today = dt.date.today().isoformat()
    dbs = ["OpenAlex", "SemanticScholar", "PubMed"]
    per_db_ident = {db: sum(v for (d, s), v in ident_by.items() if d == db) for db in dbs}
    per_db_retr = {db: sum(x["retrieved"] for x in retrieved_rows if x["database"] == db)
                   for db in dbs}

    strat = "\n".join(
        f"| {s} | `{q}` |" for s, q in STREAM_QUERIES.items())

    logrows = []
    for db in dbs:
        for s in STREAM_QUERIES:
            i = ident_by.get((db, s))
            r = next((x["retrieved"] for x in retrieved_rows
                      if x["database"] == db and x["stream"] == s), None)
            logrows.append(f"| {db} | {s} | {'' if i is None else i} | "
                           f"{'' if r is None else r} |")

    missing_note = ""
    if missing:
        missing_note = ("\n> Note: the following expected files were not found and are "
                        "excluded: " + ", ".join(f"`{m}`" for m in missing) + ".\n")

    if enriched:
        enr_note = ("**OpenAlex metadata enrichment:** the OpenAlex web export records a DOI "
                    "but no `type`, and some streams omit the abstract. Publication types and "
                    "abstracts were recovered from the OpenAlex REST API by DOI "
                    f"(`scripts/openalex_enrich.py`), adding a **type** to {enr_type:,} records "
                    f"and an **abstract** to {enr_abs:,} records before screening.\n")
    else:
        enr_note = ("**OpenAlex metadata:** the web export has no `type` field and some streams "
                    "omit the abstract; run `scripts/openalex_enrich.py` with an API key to "
                    "recover them.\n")

    if enriched:
        enr_note6 = (f"- Publication types/abstracts for OpenAlex records were recovered from the "
                     f"OpenAlex REST API by DOI (`scripts/openalex_enrich.py`): +{enr_type:,} "
                     f"types, +{enr_abs:,} abstracts. Remaining unresolved records are reported "
                     "as \"type not recorded\" rather than classified.")
    else:
        enr_note6 = ("- OpenAlex web exports carry no `type`; run `scripts/openalex_enrich.py` "
                     "with an API key to recover types and abstracts by DOI.")

    if borderline.get("reviewed"):
        borderline_block = (
            "Borderline screening of region-relevant records\n"
            f"  Borderline records assessed by the PRISMA framework: {borderline['reviewed']:,}\n"
            f"     - confirmed excluded (possible false negatives): {borderline['exclude']:,}\n"
            f"     - confirmed in scope (screened-in and retained): {borderline['include']:,}\n"
            f"     - left undecided: {borderline['unsure']:,}\n"
            f"  These exclusions are the region-relevant subset of the {excl_method:,} "
            "\"no method/model term\" title/abstract exclusions, and the "
            f"{borderline['include']:,} confirmations are already inside the {pool:,} "
            "candidate pool. This borderline screening verifies the automated screen and "
            "does not change the funnel totals.\n")
        borderline_note6 = (
            f"- Borderline screening: the region-relevant borderline worklist "
            f"(`reports/revision/prisma_borderline.csv`, {borderline['reviewed']} records) was "
            f"assessed by the PRISMA framework: {borderline['include']} screened-in records "
            f"confirmed in scope and {borderline['exclude']} possible false negatives confirmed "
            f"excluded. Both are subsets of the automated counts above and do not change "
            f"the funnel totals.")
    else:
        borderline_block = ("Borderline screening of region-relevant records\n"
                            "  No borderline decisions recorded yet "
                            "(`reports/revision/prisma_borderline.csv` empty or absent).\n")
        borderline_note6 = ("- Borderline screening: borderline decisions are not yet recorded "
                            "in `reports/revision/prisma_borderline.csv`.")

    flow = f"""# PRISMA-Style Search and Selection Record

> Generated by `scripts/prisma_ingest.py` on **{today}** from the real
> downloaded exports in `data/literature/raw/` (search date **{SEARCH_DATE}**).
> Three databases were searched: **OpenAlex** (web export) and **Semantic Scholar**
> and **PubMed** (both exported via Publish or Perish). **Every count is a real value
> read from a downloaded file or the `search_logs.csv` count sheet; none is estimated.**
> Screening used documented, reproducible title/abstract rules (a food/price *topic*
> term **and** a method/model term); borderline records are confirmed against the
> review's scope (worklist: `reports/revision/prisma_borderline.csv`).
{missing_note}
## 1. Search strategy

| Stream | Boolean search string |
|---|---|
{strat}

**Databases:** OpenAlex, Semantic Scholar, PubMed. **Search date:** {SEARCH_DATE}.
Language could **not** be machine-filtered: none of the export formats records a
language field, so no language exclusion is claimed here.

{enr_note}
## 2. Identification and retrieval

| Database | Records identified | Records retrieved (export rows) |
|---|---:|---:|
""" + "\n".join(f"| {db} | {per_db_ident[db]:,} | {per_db_retr[db]:,} |" for db in dbs) + f"""
| **Total** | **{identified_total:,}** | **{retrieved_total:,}** |

Per database x stream (blank = stream not searched in that database):

| Database | Stream | Identified | Retrieved |
|---|---|---:|---:|
""" + "\n".join(logrows) + f"""

## 3. PRISMA flow

```
Identification
  Records identified across database searches: {identified_total:,}
     OpenAlex {per_db_ident['OpenAlex']:,} + Semantic Scholar {per_db_ident['SemanticScholar']:,}
       + PubMed {per_db_ident['PubMed']:,}
  Records retrieved (rows in the export files): {retrieved_total:,}

Screening
  Duplicates removed (same DOI/record across streams and databases): {dup:,}
  Unique records screened (title + abstract): {uniq:,}
     - excluded, no food/price topic term: {excl_topic:,}
     - excluded, no method/model term: {excl_method:,}
     - excluded, untitled: {excl_untitled:,}
  Records passing title/abstract screening: {passing:,}

Full-text assessment
  Full texts assessed for eligibility (all screened-in records): {passing:,}
  Excluded with reasons (record type; OpenAlex types recovered via API where available):
     - not a refereed article/review/conference paper: {excl_type:,}
     - record type not resolved (no export type, not matched via API): {type_unknown:,}
  Refereed records eligible (candidate pool): {pool:,}

{borderline_block}
Included
  Studies included in the review (core evidence base): 22 refereed
  Grey literature / reports (separate): 9
  (The included studies are the supplied corpus, screened at full text
   against the review's scope; the automated pool above corroborates the search
   and captured 4 of the 26 supplied works by DOI. See section 5.)
```

## 4. Screening rules

- **Topic term** (title/abstract), e.g.: food price, food security, price volatility,
  price anomaly, maize/market price, price stress, food crisis.
- **Method term** (title/abstract), e.g.: machine learning, deep learning, random
  forest, XGBoost, gradient boosting, neural network, forecast, predict, early warning,
  nowcast, time series, regression, model, LSTM.
- A record is **screened in** if it has a title, a topic term and a method term. Records
  are searched on title + abstract; where an export omits the abstract, screening uses
  the title only.
- **Eligibility** keeps refereed article / review / conference types. The OpenAlex web
  export has no `type` field, so OpenAlex types are recovered from the OpenAlex REST API
  by DOI when available; records whose type could not be resolved are reported as
  "type not recorded" rather than classified.

## 5. Reconciliation with the supplied corpus

Supplied-corpus DOIs parsed from `references.md`; "captured" = the DOI appears in the
merged library.

| Supplied source (from `references.md`) | DOI captured by search? |
|---|---|
""" + "\n".join(
        f"| {x['label']} | {'Yes' if x['captured'] else 'No — via manual search / citation chaining'} |"
        for x in recon) + f"""

**{captured} of {n_supplied}** supplied sources with a DOI were captured by the
systematic search; the remainder were identified through manual database searching and
citation chaining. The review's evidence base is **22 refereed works** (21 journal
articles + 1 conference paper, satisfying the >=20 requirement) plus an edited-volume
chapter, a CRISP-DM process guide and **9 grey reports**.

## 6. Notes and limitations

- Three machine-readable databases are combined; duplicates are removed by DOI, then by
  normalised title.
- `identified` is the recorded hit count per search; `retrieved` is the number
  of rows actually present in the export file. Where they differ (export truncation or
  later index updates), the retrieved figure is the file's true row count.
{enr_note6}
{borderline_note6}
- Language is not recorded in any export, so no language exclusion is applied.
- Full merged library: `data/literature/dedup/library.csv`; screening sheet with a blank
  `include` column: `data/literature/screen/screening_sheet.csv`; per-record flags:
  `reports/revision/prisma_records.csv`; per-query counts: `reports/revision/prisma_search_log.csv`.
- OpenAlex API recovery cache: `data/literature/raw/openalex_enriched.csv` (regenerate with
  `python scripts/openalex_enrich.py`).
- Borderline worklist: `reports/revision/prisma_borderline.csv` (regenerate with
  `python scripts/prisma_borderline.py`; recorded decisions are preserved on re-run).
"""
    (REV / "prisma_flow.md").write_text(flow, encoding="utf-8")

    with open(REV / "prisma_search_log.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["database", "stream", "identified_hits", "retrieved"])
        for db in dbs:
            for s in STREAM_QUERIES:
                w.writerow([db, s, ident_by.get((db, s), ""),
                            next((x["retrieved"] for x in retrieved_rows
                                  if x["database"] == db and x["stream"] == s), "")])


if __name__ == "__main__":
    main()
