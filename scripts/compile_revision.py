"""Compile the revised chapters (markdown) into a single Word document.

Usage: python scripts/compile_revision.py
Reads reports/revision/chapter{1..5}_*.md + references.md and writes
reports/revision/Chapters_1-5_revised.docx
"""
from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
REV = ROOT / "reports" / "revision"

IMG = re.compile(r"^!\[(.+?)\]\((.+?)\)\s*$")

FILES = [
    ("chapter1_revised.md", "Chapter 1 — Introduction"),
    ("chapter2_revised.md", "Chapter 2 — Literature Review"),
    ("chapter3_revised.md", "Chapter 3 — Methodology"),
    ("chapter4_revised.md", "Chapter 4 — Results and Findings"),
    ("chapter5_revised.md", "Chapter 5 — Conclusion and Recommendations"),
    ("references.md", "References"),
    ("prisma_flow.md", "Appendix A — PRISMA Search Record"),
]

BOLD = re.compile(r"\*\*(.+?)\*\*")
ITAL = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")


def add_runs(par, text: str) -> None:
    """Add text to a paragraph, honouring **bold** and *italic*."""
    tokens = re.split(r"(\*\*.+?\*\*|(?<!\*)\*(?!\*).+?(?<!\*)\*(?!\*))", text)
    for tok in tokens:
        if not tok:
            continue
        m = BOLD.fullmatch(tok)
        if m:
            par.add_run(m.group(1)).bold = True
            continue
        m = ITAL.fullmatch(tok)
        if m:
            par.add_run(m.group(1)).italic = True
            continue
        par.add_run(tok)


def is_table_sep(line: str) -> bool:
    return bool(re.fullmatch(r"\|[\s:|-]+\|", line.strip()))


def split_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def flush_table(doc, rows: list[str]):
    grid = [split_row(r) for r in rows if not is_table_sep(r)]
    if not grid:
        return
    ncol = max(len(r) for r in grid)
    table = doc.add_table(rows=0, cols=ncol)
    table.style = "Light Grid Accent 1"
    for ri, row in enumerate(grid):
        cells = table.add_row().cells
        for ci in range(ncol):
            txt = row[ci] if ci < len(row) else ""
            cell = cells[ci]
            cell.text = ""
            add_runs(cell.paragraphs[0], txt)
            if ri == 0:
                for r in cell.paragraphs[0].runs:
                    r.bold = True


def add_image(doc, alt: str, src: str):
    """Embed an image (repo-relative path) centred, with a caption below."""
    label, _, caption = alt.partition("|")
    path = (ROOT / src.strip()).resolve()
    if not path.exists():
        doc.add_paragraph(f"[missing image: {src}]")
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(str(path), width=Inches(6.0))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = cap.add_run(label.strip() + (" " if caption else ""))
    r1.bold = True
    r2 = cap.add_run(caption.strip())
    r2.italic = True
    for r in (r1, r2):
        r.font.size = Pt(9)


def convert(doc, md_path: Path, numbered: int):
    lines = md_path.read_text(encoding="utf-8").splitlines()
    tbl_buf: list[str] = []

    def flush():
        nonlocal tbl_buf
        if tbl_buf:
            flush_table(doc, tbl_buf)
            tbl_buf = []

    for raw in lines:
        line = raw.rstrip()
        if line.startswith("|"):
            tbl_buf.append(line)
            continue
        flush()
        if not line.strip():
            continue
        img = IMG.match(line.strip())
        if img:
            add_image(doc, img.group(1), img.group(2))
        elif line.startswith(">"):
            p = doc.add_paragraph(style="Intense Quote")
            add_runs(p, line.lstrip("> ").strip())
        elif line.startswith("####"):
            doc.add_heading(line.lstrip("# ").strip(), level=4)
        elif line.startswith("###"):
            doc.add_heading(line.lstrip("# ").strip(), level=3)
        elif line.startswith("##"):
            doc.add_heading(line.lstrip("# ").strip(), level=2)
        elif line.startswith("#"):
            doc.add_heading(line.lstrip("# ").strip(), level=1)
        elif re.match(r"^\s*[-*]\s+", line):
            p = doc.add_paragraph(style="List Bullet")
            add_runs(p, re.sub(r"^\s*[-*]\s+", "", line))
        elif re.match(r"^\s*\d+\.\s+", line):
            p = doc.add_paragraph(style="List Number")
            add_runs(p, re.sub(r"^\s*\d+\.\s+", "", line))
        elif line.strip() == "---":
            doc.add_paragraph()
        else:
            p = doc.add_paragraph()
            add_runs(p, line.strip())
    flush()


def main():
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    for i, (fname, title) in enumerate(FILES):
        path = REV / fname
        if not path.exists():
            print(f"  [skip] missing {fname}")
            continue
        if i:
            doc.add_page_break()
        convert(doc, path, i)
        print(f"  [ok] {fname}")

    out = REV / "Chapters_1-5_revised.docx"
    doc.save(out)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
