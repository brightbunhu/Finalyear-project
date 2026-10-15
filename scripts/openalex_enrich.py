"""Enrich OpenAlex records with publication ``type`` and ``abstract``.

The OpenAlex **web export** used by the author records a DOI but no ``type``
and (for some streams) no abstract. This script re-queries the OpenAlex REST
API by DOI (batched, 50 per request) to recover ``type`` and the abstract for
every OpenAlex record that has a DOI, writing
``data/literature/raw/openalex_enriched.csv``. ``scripts/prisma_ingest.py``
merges this file back into the library before screening.

A free OpenAlex API key is read from the environment variable
``OPENALEX_API_KEY`` or from ``scripts/.openalex_key`` (see scripts/README.md).
The key is never written to any output file.

Run:  python scripts/openalex_enrich.py
"""
from __future__ import annotations

import csv
import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "literature" / "raw"
OUT = RAW / "openalex_enriched.csv"

MAILTO = "research@example.org"
BASE = "https://api.openalex.org/works"
BATCH = 50

OPENALEX_FILES = [
    "openalex_S1.csv", "openalex_S2.csv", "openalex3.csv",
    "openalex4.csv", "openalexS5.csv", "open alexS6.csv",
]


def api_key() -> str:
    k = os.environ.get("OPENALEX_API_KEY", "").strip()
    if k:
        return k
    f = Path(__file__).resolve().parent / ".openalex_key"
    return f.read_text(encoding="utf-8").strip() if f.exists() else ""


def clean_doi(s: str) -> str:
    import re
    s = (s or "").strip().lower()
    s = re.sub(r"^https?://(dx\.)?doi\.org/", "", s)
    s = re.sub(r"^doi:\s*", "", s)
    return s.strip().rstrip(".")


def collect_dois() -> list[str]:
    dois, seen = [], set()
    for fname in OPENALEX_FILES:
        path = RAW / fname
        if not path.exists():
            continue
        with open(path, "r", encoding="utf-8-sig", errors="replace", newline="") as f:
            rdr = csv.DictReader(f)
            cols = {c.lower().strip(): c for c in (rdr.fieldnames or [])}
            dcol = cols.get("doi")
            if not dcol:
                continue
            for row in rdr:
                doi = clean_doi(row.get(dcol) or "")
                if doi and doi not in seen:
                    seen.add(doi)
                    dois.append(doi)
    return dois


def inv_to_abstract(inv) -> str:
    if not inv:
        return ""
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def fetch(dois: list[str], key: str) -> list[dict]:
    params = {
        "filter": "doi:" + "|".join(dois),
        "per-page": str(BATCH),
        "select": "id,doi,type,title,publication_year,abstract_inverted_index",
        "mailto": MAILTO,
    }
    if key:
        params["api_key"] = key
    url = BASE + "?" + urllib.parse.urlencode(params, safe="|:")
    req = urllib.request.Request(url, headers={"User-Agent": "prisma-enrich/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8")).get("results", [])


def main():
    key = api_key()
    print("api_key:", "present" if key else "ABSENT (shared budget, may fail)")
    dois = collect_dois()
    print("openalex dois:", len(dois))

    out: dict[str, dict] = {}
    n_fail = 0
    for i in range(0, len(dois), BATCH):
        chunk = dois[i:i + BATCH]
        try:
            results = fetch(chunk, key)
        except Exception as e:  # noqa: BLE001
            n_fail += len(chunk)
            print(f"  batch {i//BATCH} error: {e}")
            time.sleep(2)
            continue
        for w in results:
            doi = clean_doi(w.get("doi", ""))
            if not doi:
                continue
            out[doi] = {
                "doi": doi,
                "type": (w.get("type") or ""),
                "title": (w.get("title") or "").replace("\n", " ").strip(),
                "year": w.get("publication_year") or "",
                "abstract": inv_to_abstract(w.get("abstract_inverted_index")),
            }
        if (i // BATCH) % 10 == 0:
            print(f"  batch {i//BATCH}: fetched={len(out)}")
        time.sleep(0.2)

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["doi", "type", "title", "year", "abstract"])
        w.writeheader()
        for rec in sorted(out.values(), key=lambda x: x["doi"]):
            w.writerow(rec)

    with_type = sum(1 for r in out.values() if r["type"])
    with_abs = sum(1 for r in out.values() if r["abstract"])
    matched = sum(1 for d in dois if d in out)
    print(f"written {OUT.relative_to(ROOT)}")
    print(f"dois_matched={matched}/{len(dois)} with_type={with_type} with_abstract={with_abs} failed={n_fail}")


if __name__ == "__main__":
    main()
