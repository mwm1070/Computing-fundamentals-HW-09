#!/usr/bin/env python3
"""Convert a Markdown file to a clean PDF using only the Python standard library.

Why this exists: the machine has pandoc but no LaTeX, wkhtmltopdf, WeasyPrint,
Chromium, or LibreOffice. This script writes the PDF directly, so `make` works
without installing anything.

Supported Markdown:
  # headings, **bold**, *italic*, `code`, [links](url), bullet and numbered
  lists, block quotes, fenced code blocks, horizontal rules, simple tables,
  and HTML comments (ignored).

Usage:
  python3 scripts/md2pdf.py paper.md output/paper.pdf
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Font metrics (AFM widths per 1000 units) for the standard PDF fonts.
# ---------------------------------------------------------------------------

HELVETICA = {
    " ": 278, "!": 278, '"': 355, "#": 556, "$": 556, "%": 889, "&": 667,
    "'": 191, "(": 333, ")": 333, "*": 389, "+": 584, ",": 278, "-": 333,
    ".": 278, "/": 278, "0": 556, "1": 556, "2": 556, "3": 556, "4": 556,
    "5": 556, "6": 556, "7": 556, "8": 556, "9": 556, ":": 278, ";": 278,
    "<": 584, "=": 584, ">": 584, "?": 556, "@": 1015, "A": 667, "B": 667,
    "C": 722, "D": 722, "E": 667, "F": 611, "G": 778, "H": 722, "I": 278,
    "J": 500, "K": 667, "L": 556, "M": 833, "N": 722, "O": 778, "P": 667,
    "Q": 778, "R": 722, "S": 667, "T": 611, "U": 722, "V": 667, "W": 944,
    "X": 667, "Y": 667, "Z": 611, "[": 278, "\\": 278, "]": 278, "^": 469,
    "_": 556, "`": 333, "a": 556, "b": 556, "c": 500, "d": 556, "e": 556,
    "f": 278, "g": 556, "h": 556, "i": 222, "j": 222, "k": 500, "l": 222,
    "m": 833, "n": 556, "o": 556, "p": 556, "q": 556, "r": 333, "s": 500,
    "t": 278, "u": 556, "v": 500, "w": 722, "x": 500, "y": 500, "z": 500,
    "{": 334, "|": 260, "}": 334, "~": 584,
}

HELVETICA_BOLD = {
    " ": 278, "!": 333, '"': 474, "#": 556, "$": 556, "%": 889, "&": 722,
    "'": 238, "(": 333, ")": 333, "*": 389, "+": 584, ",": 278, "-": 333,
    ".": 278, "/": 278, "0": 556, "1": 556, "2": 556, "3": 556, "4": 556,
    "5": 556, "6": 556, "7": 556, "8": 556, "9": 556, ":": 333, ";": 333,
    "<": 584, "=": 584, ">": 584, "?": 611, "@": 975, "A": 722, "B": 722,
    "C": 722, "D": 722, "E": 667, "F": 611, "G": 778, "H": 722, "I": 278,
    "J": 556, "K": 722, "L": 611, "M": 833, "N": 722, "O": 778, "P": 667,
    "Q": 778, "R": 722, "S": 667, "T": 611, "U": 722, "V": 667, "W": 944,
    "X": 667, "Y": 667, "Z": 611, "[": 333, "\\": 278, "]": 333, "^": 584,
    "_": 556, "`": 333, "a": 556, "b": 611, "c": 556, "d": 611, "e": 556,
    "f": 333, "g": 611, "h": 611, "i": 278, "j": 278, "k": 556, "l": 278,
    "m": 889, "n": 611, "o": 611, "p": 611, "q": 611, "r": 389, "s": 556,
    "t": 333, "u": 611, "v": 556, "w": 778, "x": 556, "y": 556, "z": 500,
    "{": 389, "|": 280, "}": 389, "~": 584,
}

# Approximate widths for common cp1252 punctuation and accented letters.
EXTRA_WIDTHS = {
    "\u2018": 222, "\u2019": 222, "\u201c": 333, "\u201d": 333,
    "\u2013": 556, "\u2014": 1000, "\u2026": 1000, "\u00a0": 278,
    "\u20ac": 556, "\u2022": 350, "\u00b7": 278,
}

PAGE_W, PAGE_H = 612.0, 792.0
MARGIN_L, MARGIN_R, MARGIN_T, MARGIN_B = 72.0, 72.0, 72.0, 72.0
BODY_SIZE = 11.0
BODY_LEADING = 15.0
CONTENT_W = PAGE_W - MARGIN_L - MARGIN_R

FONTS = {
    "F1": ("Helvetica", False, False),
    "F2": ("Helvetica-Bold", True, False),
    "F3": ("Helvetica-Oblique", False, True),
    "F4": ("Helvetica-BoldOblique", True, True),
    "F5": ("Courier", False, False),
}


def text_width(text: str, font: str, size: float) -> float:
    if font == "F5":
        return len(text) * 600.0 * size / 1000.0
    table = HELVETICA_BOLD if font in ("F2", "F4") else HELVETICA
    total = 0
    for ch in text:
        if ch in table:
            total += table[ch]
        elif ch in EXTRA_WIDTHS:
            total += EXTRA_WIDTHS[ch]
        else:
            total += 556
    return total * size / 1000.0


def clean_text(text: str) -> str:
    text = text.replace("\u00ad", "")
    text = text.replace("\u00a0", " ")
    text = text.replace("\u2011", "-")
    text = text.replace("\u2212", "-")
    text = text.replace("\u0153", "oe").replace("\u0152", "OE")
    return text


def pdf_escape(text: str) -> bytes:
    data = clean_text(text).encode("cp1252", "replace")
    out = bytearray()
    for byte in data:
        if byte in (0x28, 0x29, 0x5C):  # ( ) backslash
            out.append(0x5C)
        if byte < 32:
            out.append(0x20)
        else:
            out.append(byte)
    return bytes(out)


# ---------------------------------------------------------------------------
# Inline parsing
# ---------------------------------------------------------------------------

_INLINE_PATTERNS = [
    # Bare URLs must be protected before the emphasis patterns, or the
    # underscores in archive.org identifiers are read as italic markers.
    (re.compile(r"https?://[^\s<>]+"), "url"),
    (re.compile(r"\*\*\*(.+?)\*\*\*", re.S), "bolditalic"),
    (re.compile(r"___(.+?)___", re.S), "bolditalic"),
    (re.compile(r"\*\*(.+?)\*\*", re.S), "bold"),
    (re.compile(r"__(.+?)__", re.S), "bold"),
    (re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", re.S), "italic"),
    (re.compile(r"(?<!_)_(?!_)(.+?)(?<!_)_(?!_)", re.S), "italic"),
    (re.compile(r"`(.+?)`", re.S), "code"),
    (re.compile(r"\[([^\]]+)\]\(([^)]+)\)", re.S), "link"),
]


def font_for(bold: bool, italic: bool, code: bool) -> str:
    if code:
        return "F5"
    if bold and italic:
        return "F4"
    if bold:
        return "F2"
    if italic:
        return "F3"
    return "F1"


def parse_inline(text: str, bold: bool = False, italic: bool = False,
                 code: bool = False) -> list[tuple[str, str]]:
    """Return a list of (text, font) runs."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = text.replace("\\*", "\x00").replace("\\_", "\x01").replace("\\`", "\x02")

    runs: list[tuple[str, str]] = []
    pos = 0
    while pos < len(text):
        best = None
        for pattern, kind in _INLINE_PATTERNS:
            m = pattern.search(text, pos)
            if m and (best is None or m.start() < best[0].start()):
                best = (m, kind)
        if best is None:
            runs.append((text[pos:], font_for(bold, italic, code)))
            break

        m, kind = best
        if m.start() > pos:
            runs.append((text[pos:m.start()], font_for(bold, italic, code)))

        if kind == "bold":
            runs.extend(parse_inline(m.group(1), True, italic, code))
        elif kind == "bolditalic":
            runs.extend(parse_inline(m.group(1), True, True, code))
        elif kind == "italic":
            runs.extend(parse_inline(m.group(1), bold, True, code))
        elif kind == "url":
            runs.append((m.group(0), font_for(bold, italic, code)))
        elif kind == "code":
            runs.append((m.group(1), "F5"))
        elif kind == "link":
            label, url = m.group(1), m.group(2)
            runs.extend(parse_inline(label, bold, italic, code))
            runs.append((f" ({url})", font_for(bold, italic, code)))
        pos = m.end()

    cleaned = []
    for run_text, run_font in runs:
        run_text = run_text.replace("\x00", "*").replace("\x01", "_").replace("\x02", "`")
        if run_text:
            cleaned.append((run_text, run_font))
    return cleaned


# ---------------------------------------------------------------------------
# Wrapping
# ---------------------------------------------------------------------------

def split_long_word(word: str, font: str, size: float, max_width: float) -> list[str]:
    if text_width(word, font, size) <= max_width:
        return [word]
    pieces = []
    while word:
        lo, hi = 1, len(word)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if text_width(word[:mid], font, size) <= max_width:
                lo = mid
            else:
                hi = mid - 1
        cut = lo
        # Prefer a break at a natural boundary near the cut.
        for sep in ("/", "-", "?", "&", "=", "_", "."):
            idx = word.rfind(sep, 0, cut)
            if idx >= max(1, cut // 2):
                cut = idx + 1
                break
        pieces.append(word[:cut])
        word = word[cut:]
    return pieces


def runs_to_tokens(runs: list[tuple[str, str]]) -> list[tuple[str, str, bool]]:
    """Tokenize runs into (word, font, space_before) triples.

    The space flag preserves punctuation next to a formatting boundary: in
    ``**bold**,`` the comma has no space before it, so it stays attached.
    """
    tokens: list[tuple[str, str, bool]] = []
    pending_space = False
    for run_text, run_font in runs:
        for part in re.split(r"(\s+)", run_text):
            if not part:
                continue
            if part.isspace():
                pending_space = True
            else:
                tokens.append((part, run_font, pending_space))
                pending_space = False
    return tokens


def wrap_tokens(tokens: list[tuple[str, str, bool]], size: float,
                max_width: float) -> list[list[tuple[str, str]]]:
    lines: list[list[tuple[str, str]]] = []
    current: list[tuple[str, str]] = []
    current_w = 0.0
    space_w = text_width(" ", "F1", size)

    for word, font, space_before in tokens:
        pieces = split_long_word(word, font, size, max_width)
        for index, piece in enumerate(pieces):
            piece_w = text_width(piece, font, size)
            needs_space = index == 0 and space_before
            if current and needs_space and current_w + space_w + piece_w > max_width:
                lines.append(current)
                current = []
                current_w = 0.0
            if current and not needs_space and current_w + piece_w > max_width:
                lines.append(current)
                current = []
                current_w = 0.0
            if current and needs_space:
                current.append((" ", "F1"))
                current_w += space_w
            current.append((piece, font))
            current_w += piece_w

    if current:
        lines.append(current)
    return lines


# ---------------------------------------------------------------------------
# PDF document builder
# ---------------------------------------------------------------------------

class PDF:
    def __init__(self) -> None:
        self.pages: list[list[bytes]] = []
        self.page: list[bytes] = []
        self.y = PAGE_H - MARGIN_T

    def new_page(self) -> None:
        if self.page:
            self.pages.append(self.page)
        self.page = []
        self.y = PAGE_H - MARGIN_T

    def ensure(self, height: float) -> None:
        if self.y - height < MARGIN_B:
            self.new_page()

    def _text_line(self, runs: list[tuple[str, str]], x: float, y: float,
                   size: float) -> bytes:
        parts = [b"BT", f"/F1 {size:.2f} Tf".encode(),
                 f"1 0 0 1 {x:.2f} {y:.2f} Tm".encode()]
        current_font = "F1"
        for run_text, run_font in runs:
            if not run_text:
                continue
            if run_font != current_font:
                parts.append(f"/{run_font} {size:.2f} Tf".encode())
                current_font = run_font
            parts.append(b"(" + pdf_escape(run_text) + b") Tj")
        parts.append(b"ET")
        return b" ".join(parts)

    def add_runs(self, runs: list[tuple[str, str]], size: float = BODY_SIZE,
                 leading: float = BODY_LEADING, indent: float = 0.0,
                 hanging: float = 0.0, space_after: float = 6.0,
                 max_width: float | None = None) -> None:
        width = (max_width if max_width is not None else CONTENT_W) - indent - hanging
        lines = wrap_tokens(runs_to_tokens(runs), size, width)
        for index, line in enumerate(lines):
            self.ensure(leading)
            x = MARGIN_L + indent + (0.0 if index == 0 else hanging)
            self.page.append(self._text_line(line, x, self.y, size))
            self.y -= leading
        self.y -= space_after

    def add_paragraph(self, text: str, size: float = BODY_SIZE,
                      leading: float = BODY_LEADING, indent: float = 0.0,
                      space_after: float = 6.0) -> None:
        self.add_runs(parse_inline(text), size, leading, indent=indent,
                      space_after=space_after)

    def add_heading(self, level: int, text: str) -> None:
        sizes = {1: 20.0, 2: 14.0, 3: 12.0, 4: 11.0, 5: 11.0, 6: 11.0}
        before = {1: 0.0, 2: 16.0, 3: 12.0, 4: 10.0, 5: 8.0, 6: 8.0}
        after = {1: 10.0, 2: 6.0, 3: 5.0, 4: 4.0, 5: 4.0, 6: 4.0}
        size = sizes.get(level, 11.0)
        leading = size * 1.25
        self.ensure(before.get(level, 8.0) + leading)
        self.y -= before.get(level, 8.0)
        runs = parse_inline(text, bold=True)
        lines = wrap_tokens(runs_to_tokens(runs), size, CONTENT_W)
        for line in lines:
            self.ensure(leading)
            self.page.append(self._text_line(line, MARGIN_L, self.y, size))
            self.y -= leading
        self.y -= after.get(level, 4.0)

    def add_bullet(self, text: str, marker: str = "\u2022") -> None:
        runs = [(marker + " ", "F1")] + parse_inline(text)
        self.add_runs(runs, indent=18.0, hanging=14.0, space_after=3.0)

    def add_number(self, number: str, text: str) -> None:
        runs = [(f"{number}. ", "F1")] + parse_inline(text)
        self.add_runs(runs, indent=22.0, hanging=18.0, space_after=3.0)

    def add_quote(self, text: str) -> None:
        runs = parse_inline(text, italic=True)
        self.add_runs(runs, size=10.5, leading=14.0, indent=24.0,
                      space_after=8.0)

    def add_code(self, lines: list[str]) -> None:
        self.y -= 2
        for line in lines:
            for chunk_start in range(0, max(1, len(line)), 88):
                chunk = line[chunk_start:chunk_start + 88]
                self.ensure(11.0)
                self.page.append(self._text_line([(chunk, "F5")],
                                                 MARGIN_L + 12.0, self.y, 9.0))
                self.y -= 11.0
        self.y -= 8

    def add_hr(self) -> None:
        self.ensure(10.0)
        self.y -= 4.0
        self.page.append(
            f"0.7 0.7 0.7 RG 0.6 w {MARGIN_L:.2f} {self.y:.2f} m "
            f"{PAGE_W - MARGIN_R:.2f} {self.y:.2f} l S".encode()
        )
        self.y -= 10.0

    def add_table_row(self, cells: list[str]) -> None:
        text = " | ".join(cell.strip() for cell in cells)
        self.add_paragraph(text, size=10.0, leading=13.0, space_after=2.0)

    def finish(self) -> list[list[bytes]]:
        if self.page:
            self.pages.append(self.page)
            self.page = []
        total = len(self.pages)
        for index, page in enumerate(self.pages, 1):
            label = str(index)
            x = (PAGE_W - text_width(label, "F1", 9.0)) / 2.0
            page.append(
                b"BT /F1 9.00 Tf 0.45 0.45 0.45 rg "
                + f"1 0 0 1 {x:.2f} 36.00 Tm".encode()
                + b" (" + label.encode() + b") Tj ET"
            )
        return self.pages


# ---------------------------------------------------------------------------
# Markdown block parser
# ---------------------------------------------------------------------------

def strip_comments(lines: list[str]) -> list[str]:
    text = "\n".join(lines)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    return text.split("\n")


def parse_blocks(lines: list[str]):
    blocks = []
    i, n = 0, len(lines)
    while i < n:
        stripped = lines[i].strip()
        if not stripped:
            i += 1
            continue
        if stripped.startswith("<!--"):
            while i < n and "-->" not in lines[i]:
                i += 1
            i += 1
            continue

        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            blocks.append(("heading", len(m.group(1)), m.group(2).strip()))
            i += 1
            continue

        if re.match(r"^(\*{3,}|-{3,}|_{3,})$", stripped):
            blocks.append(("hr",))
            i += 1
            continue

        if stripped.startswith("```"):
            i += 1
            code_lines = []
            while i < n and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i].rstrip("\n"))
                i += 1
            i += 1
            blocks.append(("code", code_lines))
            continue

        if stripped.startswith(">"):
            quote = []
            while i < n and lines[i].strip().startswith(">"):
                q = lines[i].strip()[1:]
                if q.startswith(" "):
                    q = q[1:]
                quote.append(q)
                i += 1
            blocks.append(("quote", " ".join(quote)))
            continue

        if re.match(r"^[-*+]\s+", stripped):
            items = []
            while i < n and re.match(r"^[-*+]\s+", lines[i].strip()):
                items.append(lines[i].strip()[2:].strip())
                i += 1
            blocks.append(("bullets", items))
            continue

        if re.match(r"^\d+[.)]\s+", stripped):
            items = []
            while i < n and re.match(r"^\d+[.)]\s+", lines[i].strip()):
                m2 = re.match(r"^(\d+)[.)]\s+(.*)$", lines[i].strip())
                items.append((m2.group(1), m2.group(2).strip()))
                i += 1
            blocks.append(("numbers", items))
            continue

        # Simple pipe table
        if "|" in stripped and i + 1 < n and re.match(
                r"^\s*\|?[\s:|-]+\|[\s:|-]*$", lines[i + 1]):
            rows = []
            while i < n and "|" in lines[i]:
                row = lines[i].strip()
                if re.match(r"^\|?[\s:|-]+\|[\s:|-]*$", row):
                    i += 1
                    continue
                cells = [c.strip() for c in row.strip("|").split("|")]
                rows.append(cells)
                i += 1
            blocks.append(("table", rows))
            continue

        para = [stripped]
        i += 1
        while i < n:
            nxt = lines[i].strip()
            if not nxt:
                break
            if re.match(r"^(#{1,6})\s+", nxt):
                break
            if nxt.startswith(">") or nxt.startswith("```"):
                break
            if re.match(r"^[-*+]\s+", nxt) or re.match(r"^\d+[.)]\s+", nxt):
                break
            if re.match(r"^(\*{3,}|-{3,}|_{3,})$", nxt):
                break
            para.append(nxt)
            i += 1
        blocks.append(("para", " ".join(para)))
    return blocks


# ---------------------------------------------------------------------------
# PDF output
# ---------------------------------------------------------------------------

def write_pdf(pages: list[list[bytes]], path: Path, title: str) -> None:
    n = len(pages)
    page_start = 9
    content_start = page_start + n
    total_objects = content_start + n - 1

    objects: list[bytes] = [b""] * (total_objects + 1)

    objects[1] = b"<< /Type /Catalog /Pages 2 0 R >>"
    kids = " ".join(f"{page_start + i} 0 R" for i in range(n))
    objects[2] = f"<< /Type /Pages /Kids [{kids}] /Count {n} >>".encode()
    for idx, (name, bold, italic) in enumerate(FONTS.values(), start=3):
        objects[idx] = (
            f"<< /Type /Font /Subtype /Type1 /BaseFont /{name} "
            f"/Encoding /WinAnsiEncoding >>"
        ).encode()
    objects[8] = (
        b"<< /Title (" + pdf_escape(title) + b") "
        b"/Producer (md2pdf.py) /Creator (md2pdf.py) >>"
    )

    for i, page in enumerate(pages):
        content = b"\n".join(page)
        content_obj = content_start + i
        objects[content_obj] = (
            f"<< /Length {len(content)} >>\nstream\n".encode()
            + content
            + b"\nendstream"
        )
        objects[page_start + i] = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 3 0 R /F2 4 0 R /F3 5 0 R "
            f"/F4 6 0 R /F5 7 0 R >> >> /Contents {content_obj} 0 R >>"
        ).encode()

    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0] * (total_objects + 1)
    for idx in range(1, total_objects + 1):
        offsets[idx] = len(out)
        out += f"{idx} 0 obj\n".encode()
        out += objects[idx]
        out += b"\nendobj\n"

    xref = len(out)
    out += f"xref\n0 {total_objects + 1}\n".encode()
    out += b"0000000000 65535 f \n"
    for idx in range(1, total_objects + 1):
        out += f"{offsets[idx]:010d} 00000 n \n".encode()
    out += (
        f"trailer\n<< /Size {total_objects + 1} /Root 1 0 R /Info 8 0 R >>\n"
        f"startxref\n{xref}\n%%EOF\n"
    ).encode()

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(bytes(out))


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("Usage: python3 scripts/md2pdf.py INPUT.md OUTPUT.pdf", file=sys.stderr)
        return 2

    source = Path(argv[1])
    target = Path(argv[2])
    if not source.exists():
        print(f"Input not found: {source}", file=sys.stderr)
        return 1

    raw_lines = source.read_text(encoding="utf-8").splitlines()
    lines = strip_comments(raw_lines)
    blocks = parse_blocks(lines)

    pdf = PDF()
    title = "Document"
    first_heading = True

    for block in blocks:
        kind = block[0]
        if kind == "heading":
            level, text = block[1], block[2]
            if level == 1 and first_heading:
                title = text
                first_heading = False
            pdf.add_heading(level, text)
        elif kind == "para":
            pdf.add_paragraph(block[1])
        elif kind == "bullets":
            for item in block[1]:
                pdf.add_bullet(item)
            pdf.y -= 4
        elif kind == "numbers":
            for number, item in block[1]:
                pdf.add_number(number, item)
            pdf.y -= 4
        elif kind == "quote":
            pdf.add_quote(block[1])
        elif kind == "code":
            pdf.add_code(block[1])
        elif kind == "hr":
            pdf.add_hr()
        elif kind == "table":
            for row in block[1]:
                pdf.add_table_row(row)
            pdf.y -= 4

    pages = pdf.finish()
    write_pdf(pages, target, title)
    print(f"Wrote {target} ({len(pages)} page(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
