"""Human borderline worklist for the PRISMA screening (multi-database flow).

The automated screening in ``scripts/prisma_ingest.py`` uses documented keyword
rules (a food/price *topic* term **and** a method/model term). This script
exports the **small set of records that sit near the decision boundary and could
change the review's evidence base**, restricted to those most relevant to the
review's scope (Zimbabwe / Southern Africa market food price stress), so a human
can confirm them quickly.

It reads ``reports/revision/prisma_records.csv`` and writes
``reports/revision/prisma_borderline.csv`` with empty ``human_decision``
(Include / Exclude / Unsure) and ``human_notes`` columns to fill in.

Two targeted groups (each row tagged in ``category``):

  G1_confirm_region_include
      A refereed record that SCREENED IN and is region-relevant
      (Zimbabwe / Southern Africa in the title) -> confirm it is genuinely in
      scope (the human confirms *includes*, not only excludes).

  G2_check_region_false_negative
      A refereed record that was EXCLUDED because it has a food/price term in
      the title but no method/model term, and is region-relevant -> the most
      plausible FALSE NEGATIVES. Action: decide Include / Exclude.

Offline: reads reports/revision/prisma_records.csv.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

REV = Path(__file__).resolve().parents[1] / "reports" / "revision"

REGION = ["zimbabwe", "southern africa", "sadc", "zambia", "malawi", "mozambique",
          "south africa", "harare", "bulawayo", "mutare", "gweru", "masvingo",
          "matabeleland", "manicaland", "midlands"]


def main():
    d = pd.read_csv(REV / "prisma_records.csv", dtype=str, keep_default_na=False)
    b = lambda c: d[c].str.lower().eq("true")  # noqa: E731
    si, ti, mt, ref = b("screened_in"), b("screen_topic"), b("screen_method"), b("refereed")
    ttl = d["title"].str.lower()
    region = ttl.apply(lambda s: any(k in s for k in REGION))

    parts = []

    g1 = d[si & ref & region].copy()
    g1["category"] = "G1_confirm_region_include"
    g1["suggested"] = "Keep"
    parts.append(g1)

    g2 = d[~si & ref & ti & ~mt & region].copy()
    g2["category"] = "G2_check_region_false_negative"
    g2["suggested"] = "Likely exclude"
    parts.append(g2)

    out = pd.concat(parts, ignore_index=True).drop_duplicates(subset=["doi", "title"])
    out["human_decision"] = ""   # Include / Exclude / Unsure
    out["human_notes"] = ""

    # Preserve any human decisions already recorded (keyed by DOI, else title).
    dest = REV / "prisma_borderline.csv"
    if dest.exists():
        prev = pd.read_csv(dest, dtype=str, keep_default_na=False)
        key = lambda df: df["doi"].where(df["doi"].ne(""), df["title"])  # noqa: E731
        prev_map = {k: (dc, nt) for k, dc, nt in
                    zip(key(prev), prev["human_decision"], prev["human_notes"])}
        for i in out.index:
            k = out.at[i, "doi"] or out.at[i, "title"]
            if k in prev_map:
                out.at[i, "human_decision"], out.at[i, "human_notes"] = prev_map[k]

    keep = ["category", "suggested", "human_decision", "human_notes",
            "title", "year", "type", "doi", "source", "databases", "streams"]
    out = out[keep].sort_values(["category", "year"], ascending=[True, False])
    out.to_csv(dest, index=False)

    print("borderline records:", len(out))
    print(out["category"].value_counts().to_string())
    print("Wrote reports/revision/prisma_borderline.csv")


if __name__ == "__main__":
    main()
