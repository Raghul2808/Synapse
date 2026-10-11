# IEEE Conference Template Distillation Contract

## Reference

- Retained source: `/home/fykern/Downloads/conference-template-letter.docx`
- SHA-256: `4589779a1a74782dc5a7a657a9907f243c9dd54510cb6c154acaf24cc9079852`
- Rendered evidence: `.report_work/ieee_template_distill/template-reference-render/page-1.png` through `page-3.png`
- Rendered pages: 3; one section, portrait, US Letter (612 by 792 pt). The requested deliverable explicitly changes the page size to A4.
- The source uses OOXML strict relationship URIs (`purl.oclc.org`) that the supplied `python-docx` audits do not parse. Visual rendering and read-only ZIP/XML inspection were used instead.

## Page System

- Source geometry: Letter portrait; top 54 pt, right 44.65 pt, bottom 72 pt, left 44.65 pt; two columns with 36 pt inter-column space.
- Target geometry: A4 portrait with IEEE two-column layout: 0.75 in side margins, 0.75 in top/bottom margins, 0.25 in column gap. The full-width title, author, abstract, and keyword block precedes two-column body text on page 1.
- No page header or page number is used in the conference body. Footer template boilerplate and funding footnote are to be removed.

## Typography and Structure

- Typeface: Times New Roman visual equivalent. Title: 24 pt centered. Authors: 11 pt centered. Affiliation: 10 pt centered. Body: 9 pt justified, first-line 0.2 in indent, approximately 11.4 pt leading.
- Abstract and keywords: 9 pt; bold italic lead-in followed by body text; full width before the columns.
- Level 1 heads: centered, small caps / uppercase Roman-numeral form (`I. INTRODUCTION`). Level 2 heads: italic, left aligned, uppercase alphabetical form (`A. Data Architecture`).
- Component heads: centered, unnumbered, upper case (`ACKNOWLEDGMENT`, `REFERENCES`).
- Citations: bracketed numeric citations. References: 8 pt with hanging indent.

## Components and Slot Map

- Full-width slots: title (no symbols or footnotes), two author blocks, abstract, keywords.
- Body slots: required sections I-VII; one algorithm table; one architecture figure placeholder; one Jaccard equation with consecutive number flush right; unnumbered acknowledgment and reference list.
- Figure: bordered placeholder rectangle with a concise description; caption below as `Fig. 1.`.
- Table: caption above as `TABLE I`; compact ruled grid and 7.5-8 pt type.
- The template's instructional prose, red warning, sample content, placeholder author instructions, footer, and template reference examples are all excluded.

## Fidelity Gates

- Preserve the template's visual IEEE conference hierarchy, two-column body, Times typography, figure/table caption convention, and reference style.
- Apply the explicit A4 request rather than the source Letter page size.
- Render every final PDF page at normal print scale and inspect for clipped text, column overflow, unbalanced pages, and missing equation/caption content.
