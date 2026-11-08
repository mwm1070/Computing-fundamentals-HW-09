# Research Log

**Project:** Computing Fundamentals Assignment 09 — time-travel research paper comparing the VOC and the EIC, 1725–1750.

**Working directory:** `/home/m1k3y/Computing-fundamentals-assignment-09`

**Purpose of this log.** The assignment requires a record of the research process: the tools used, the sources found, the claims verified, and the revisions made. This log is that record. It is also evidence that the paper was built from sources rather than generated in one pass.

---

## 7 November 2026 — audit of the earlier repository

**Task:** Review the deleted/old assignment repo and identify what needed to be rebuilt.

**Findings:**
- The paper body was about 1,505 words, over the 1,500-word ceiling.
- The notes were about 1,121 words, well under the “at least twice the paper” requirement.
- The bibliography had 12 entries, but only 6 had links, and the links were generic homepages rather than direct documents.
- The Makefile was misnamed `MD2pdf script` and did not build reliably.
- All six source PDFs were secondary and in English. There were no period primary sources and no non-English sources.
- The draft’s claim that 1748–50 was a “post-war peak” was not supported by the sources.

**Decision:** Rebuild the repo from scratch with a proper evidence base: page-level source notes, a quote bank, a chronology, a paragraph outline, a refutation pass, and a bibliography with direct links.

---

## 8 November 2026 — source extraction and gap analysis

**Task:** Extract page-level text from the six existing PDFs and identify what was missing.

**Tools:** `pypdf` 7.0.0 (unpacked locally to `/tmp/opencode/pylibs`), Python 3, `grep`.

**What I did:**
- Extracted every page of the six PDFs into text files with `=== PAGE N ===` markers.
- Read the abstracts and key sections of Zheng, Nogués-Marco, Phung, Rousseau, Price & Whatley, and Taylor.
- Built a keyword index for “dividend,” “yield,” “1725,” “1750,” “liquidity,” “slavery,” “1762,” and “decline.”

**What I found:**
- The six PDFs were all secondary and English. They could support the financial argument but not the primary-source or non-English requirements.
- Zheng gave the VOC cost and dividend figures, but not the EIC comparison.
- Nogués-Marco gave the EIC’s India bond coupons, but not a share-price series.
- Phung gave the VOC liquidity collapse, but only through 1729.
- Rousseau gave the Amsterdam market context, but not a company comparison.
- Price & Whatley gave the slavery-finance link, but not the EIC.
- Taylor gave the long-run return data and the 1762 lows, which refuted the “1748–50 peak” claim.

**Gap:** I needed period primary sources, non-English sources, and a company-level cash-out context.

---

## 8 November 2026 — primary and non-English source discovery

**Task:** Find and verify sources that meet the assignment’s primary and language requirements.

**Tools:** Web search, archive.org, Nationaal Archief, Huygens Institute, Wikisource, `curl`.

**Sources found and verified:**
- **1727:** *A Letter to the Chairman of the East-India Company* — a period pamphlet by an EIC proprietor. Archive.org.
- **1730:** *A Collection of Papers Relating to the East India Trade* — a free-trade critique of the EIC monopoly. Archive.org.
- **1749:** *Three Letters to the Proprietors of Stock in the East-India Company* — a pamphlet printed for the January 3, 1749 proprietors’ ballot. Archive.org.
- **1741/1763:** Van Imhoff, *Considérations sur l’état présent de la Compagnie Hollandoise des Indes Orientales* — the Governor-General’s diagnosis of decline, in French. Archive.org.
- **1688:** De la Vega, *Confusión de Confusiones* — the classic contemporary account of the Amsterdam bourse, in Spanish. Archive.org / Koninklijke Bibliotheek.
- **1602:** *Octrooi van de VOC* — the charter, in Dutch. Nationaal Archief and Wikisource.
- **1693–1701:** Van Dam, *Beschryvinge van de Oostindische Compagnie* — the VOC’s internal description, in Dutch. Huygens Institute.
- **1742:** Savary des Bruslons, *Dictionnaire universel de commerce* — a French commercial dictionary. Archive.org.

**Verification:**
- Every link was tested and returns the document described, not a homepage.
- The page numbers and quotations were checked against the extracted text or the page images.
- The 1730 PDF downloaded truncated on the first attempt; I resumed the download and confirmed it opens with 135 pages.
- The De la Vega PDF download failed on the first attempt (170 bytes); I retried and confirmed a 406-page PDF.

**What I could not find:**
- A free, digitized run of *The Course of the Exchange* for 1725–50. It is behind library databases (ECCO, British Library). Nogués-Marco’s appendix and Taylor’s market-level series are the practical substitutes.
- The Dutch original of Van Imhoff’s 1741 memorandum. I used the 1763 French translation.
- A direct quotation from Van Dam’s Dutch text. I used it for institutional context only.

---

## 8 November 2026 — evidence base and outline

**Task:** Turn the sources into a usable evidence base for the paper.

**Outputs:**
- `notes/01-source-notes.md` — 7,800+ words of source-by-source notes with page numbers, quotations, translations, and limitations.
- `notes/02-quote-bank.md` — 26 quotations with citations, translations, and cautions.
- `notes/03-chronology.md` — a timeline from 1600 to 1799, with the 1725–50 window in detail.
- `notes/04-outline.md` — a paragraph-by-paragraph outline for a 1,400-word paper.
- `notes/05-refutation-pass.md` — an audit of the earlier draft’s claims, the strongest objections to the new thesis, and a revision checklist.
- `notes/06-bibliography.md` — 14 annotated sources with direct links and a primary/non-English ratio table.

**Key decisions:**
- **No “1748–50 peak.”** Taylor’s data show a secular decline from 1721 to 1763, with new lows in 1762. The paper will use “least-bad exit window” instead of “peak.”
- **No “EIC was ethical.”** The EIC was a chartered monopoly, and the British financial revolution was entangled with slavery. The paper will argue that the EIC was the better *financial* bet of two bad options, not a moral one.
- **No invented prices.** The 1749 pamphlet gives the decision context, not a share price. The paper will recommend a window, not a number.
- **Separate the dividend from the total return.** The VOC’s 18% average dividend was funded by borrowing; it was compensation for risk, not a sign of health.

---

## What remains

1. **Write the paper.** The student writes the prose, using the outline and the quote bank. The assistant does not write the paper under Plan A.
2. **Verify every quotation.** Check each quotation against the page image. The notes flag OCR problems and modernized spellings.
3. **Choose the final bibliography.** Cite at least 10 sources; include at least half primary and at least two non-English.
4. **Build the PDF.** Run `make` (the build script is pure Python and has no external dependencies).
5. **Run the word count.** `make count` prints the body word count; the target is 1,400.
6. **Commit in stages.** Commit the notes, then the paper, then the build script, so the history shows the process.
7. **Push to GitHub.** Create a new repository under `mwm1070` and push. Do not reuse the old repo or the exposed token.

---

## Tools used

- **OpenCode** (this session) for source discovery, extraction, summarization, outline, and refutation.
- **Gemini** (student’s research) for independent source discovery and comparison.
- **Web search** for archive.org, Nationaal Archief, Huygens, and CFA Institute links.
- **pypdf 7.0.0** for page-level PDF extraction.
- **curl** for downloading the source PDFs.
- **pandoc** (available) for checking the Markdown; the PDF build uses a pure-Python script because no LaTeX/Chromium/WeasyPrint engine is installed.

---

## Problems and fixes

| Problem | Fix |
|---|---|
| 1730 PDF downloaded truncated (62 MB of 82 MB) | Resumed with `curl -C -`; confirmed 135 pages. |
| De la Vega PDF downloaded as 170 bytes | Deleted and retried with a browser user agent; confirmed 406 pages. |
| No `pdflatex`, `wkhtmltopdf`, `weasyprint`, or Chromium | Wrote a pure-Python Markdown-to-PDF script with no external dependencies. |
| Nogués-Marco DOI returns 403 to automated requests | The DOI is correct; Cambridge blocks bots. Use a browser or the local PDF. |
| No free *Course of the Exchange* for 1725–50 | Use Nogués-Marco’s appendix and Taylor’s market-level series; do not invent a price. |
| Old paper over the word limit and notes too short | Rebuilt the notes at 7,800+ words and the outline at 1,400 words. |

---

## A note on the old repository

The old repository was deleted, so this is a fresh repo. Do not restore the old `.git` history: it contains the earlier draft’s unsupported “peak” claim and a bibliography with generic links. The new history should show the research process: notes first, paper second, build script third.
