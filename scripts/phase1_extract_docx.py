"""Phase 1 helper: extract paragraphs and tables from the dissertation DOCX.

Outputs a plain-text mirror (with table markers) so the text can be inspected
without Word. This is a lossless-as-possible read-only extraction; it does not
modify the source document.
"""
from __future__ import annotations

import sys
from pathlib import Path

from docx import Document

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "Chapter 1-5.docx"
OUT_DIR = ROOT / "reports"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def iter_block_items(document):
    """Yield paragraphs and tables in document order."""
    from docx.document import Document as _Doc
    from docx.oxml.table import CT_Tbl
    from docx.oxml.text.paragraph import CT_P
    from docx.table import Table, _Cell
    from docx.text.paragraph import Paragraph

    parent = document.element.body
    for child in parent.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, document)
        elif isinstance(child, CT_Tbl):
            yield Table(child, document)


def main() -> int:
    if not SRC.exists():
        print(f"ERROR: not found: {SRC}")
        return 1
    doc = Document(str(SRC))

    lines: list[str] = []
    n_para = 0
    n_table = 0
    for block in iter_block_items(doc):
        if block.__class__.__name__ == "Paragraph":
            text = block.text
            style = block.style.name if block.style is not None else ""
            if text.strip():
                lines.append(f"[{style}] {text}")
                n_para += 1
        else:  # Table
            n_table += 1
            lines.append(f"\n===== TABLE {n_table} =====")
            for row in block.rows:
                cells = [c.text.replace("\n", " | ").strip() for c in row.cells]
                lines.append(" || ".join(cells))
            lines.append("===== END TABLE =====\n")

    out = OUT_DIR / "dissertation_extracted.txt"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"paragraphs={n_para} tables={n_table} chars={sum(len(l) for l in lines)}")
    print(f"written: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
