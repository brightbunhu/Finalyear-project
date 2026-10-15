"""Phase 2 - Human borderline worklist for the PRISMA screening.

The automated screening in `phase2_prisma.py` uses keyword rules. This script exports
the **small set of records that sit near the decision boundary and could change the
review's included set**, so a human can confirm them. It writes
reports/revision/prisma_borderline.csv with empty `human_decision`
(Include / Exclude / Unsure) and `human_notes` columns to fill in.

Two targeted groups (each row tagged with `borderline_reason`):

  P1 refereed_food_title_excluded
       A refereed article with a food/price term *in the title* that the keyword
       screen nonetheless excluded -> the most likely FALSE NEGATIVES.
       Action: decide Include / Exclude.

  P2 grey_eligible_food_title
       A non-refereed record (preprint / report / book chapter / dissertation) that
       passed topic+method+English AND has a food/price term in the title
       -> a plausible GREY-LITERATURE include.
       Action: decide Include (as grey) / Exclude.

Reference counts (for context, not exported here) in the full retrieval:
  eligible preprints ......... 232
  eligible book chapters ..... 214
  eligible reports ........... 64

Offline: reads reports/revision/prisma_records.csv (produced by phase2_prisma.py).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

REV = Path(__file__).resolve().parents[1] / "reports" / "revision"
REFEREED = {"article", "review", "conference-paper"}
FOOD = ["food price", "food prices", "price volatility", "price anomaly", "price spike",
        "commodity price", "maize price", "market price", "cereal price", "staple price",
        "food insecurity", "price stress"]


def main():
    d = pd.read_csv(REV / "prisma_records.csv")
    d["refereed_v"] = d["type"].isin(REFEREED)
    t = d["screen_topic"].astype(bool)
    m = d["screen_method"].astype(bool)
    lang = d["screen_lang"].astype(bool)
    titled = d["title"].fillna("").str.strip().ne("")
    d["food_title"] = d["title"].fillna("").str.lower().apply(
        lambda s: any(k in s for k in FOOD))
    eligible = t & m & lang & titled

    parts = []
    p1 = d[d["refereed_v"] & d["food_title"] & ~eligible].copy()
    p1["borderline_reason"] = "P1 refereed_food_title_excluded"
    parts.append(p1)

    p2 = d[~d["refereed_v"] & eligible & d["food_title"]].copy()
    p2["borderline_reason"] = "P2 grey_eligible_food_title"
    parts.append(p2)

    out = pd.concat(parts, ignore_index=True).drop_duplicates(subset=["id"])
    out["human_decision"] = ""   # Include / Exclude / Unsure
    out["human_notes"] = ""
    keep = ["borderline_reason", "title", "year", "type", "language", "doi", "venue",
            "id", "human_decision", "human_notes"]
    out = out[keep].sort_values(["borderline_reason", "year"], ascending=[True, False])
    out.to_csv(REV / "prisma_borderline.csv", index=False)

    print("borderline records:", len(out))
    print(out["borderline_reason"].value_counts().to_string())
    print("Wrote prisma_borderline.csv")


if __name__ == "__main__":
    main()
