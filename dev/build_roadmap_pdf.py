# -*- coding: utf-8 -*-
"""ROADMAP.md → ROADMAP.pdf (A4 paysage pour les tableaux larges).

Usage : python3 dev/build_roadmap_pdf.py  [sortie.pdf]
"""
import base64
import os
import sys

import markdown
import weasyprint

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "ROADMAP.md")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "docs", "ROADMAP.pdf")
LOGO = os.path.join(ROOT, "docs", "logo_aite.jpg")

md = open(SRC, encoding="utf-8").read()
body = markdown.markdown(md, extensions=["tables", "fenced_code", "sane_lists"])
logo = ""
if os.path.exists(LOGO):
    logo = '<img class="logo" src="data:image/jpeg;base64,%s"/>' % base64.b64encode(
        open(LOGO, "rb").read()).decode()

CSS = """
@page { size: A4 landscape; margin: 14mm 12mm 16mm 12mm;
  @bottom-left { content: "AITE HOUSE — Roadmap produit · 11 octobre 2026"; font-size: 7.5pt; color: #777; }
  @bottom-right { content: "page " counter(page) " / " counter(pages); font-size: 7.5pt; color: #777; } }
body { font-family: "DejaVu Sans", Arial, sans-serif; font-size: 8.6pt; color: #1f2933; line-height: 1.38; }
h1 { font-size: 19pt; color: #5b2a86; margin: 0 0 2mm 0; }
h2 { font-size: 12.5pt; color: #5b2a86; border-bottom: 0.5mm solid #5b2a86; padding-bottom: 1mm; margin: 7mm 0 3mm 0; page-break-after: avoid; }
h3 { font-size: 10pt; color: #0f6478; margin: 5mm 0 2mm 0; page-break-after: avoid; }
table { border-collapse: collapse; width: 100%; margin: 2mm 0 4mm 0; page-break-inside: auto; }
th { background: #5b2a86; color: #fff; text-align: left; padding: 1.6mm 2mm; font-size: 8pt; }
td { border-bottom: 0.2mm solid #d9dee3; padding: 1.5mm 2mm; vertical-align: top; }
tr { page-break-inside: avoid; }
tr:nth-child(even) td { background: #f6f3fa; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: 7.8pt; background: #eef0f3; padding: 0 0.6mm; border-radius: 0.6mm; }
.logo { height: 13mm; float: right; }
hr { border: 0; border-top: 0.3mm solid #ccc; margin: 4mm 0; }
ul, ol { margin: 1mm 0 2mm 0; padding-left: 5mm; }
li { margin-bottom: 0.6mm; }
p { margin: 1.2mm 0; }
"""
html = "<html><head><meta charset='utf-8'><style>%s</style></head><body>%s%s</body></html>" % (
    CSS, logo, body)
weasyprint.HTML(string=html).write_pdf(OUT)
print("écrit", OUT)
