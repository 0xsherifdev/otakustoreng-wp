#!/usr/bin/env python3
"""Render info-page workflow output -> content/03_STANDARD_PAGES.txt (paste-ready)."""
import json, sys, re, os

RAW = sys.argv[1]
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "content", "03_STANDARD_PAGES.txt")

CUR_RE = re.compile(r"&#8377;|&#x20b9;|&#8358;|&#x20a6;|₹")
def fix_cur(s):
    return CUR_RE.sub("₦", s) if isinstance(s, str) else s

def trim(s, n):
    if len(s) <= n:
        return s
    cut = s[:n]; sp = cut.rfind(" ")
    if sp > n * 0.6: cut = cut[:sp]
    return cut.rstrip(" .,-—") + "."

raw = json.load(open(RAW, encoding="utf-8"))
res = raw["result"] if isinstance(raw, dict) and "result" in raw else raw

ORDER = ["about", "contact", "track-order", "size-guide", "shipping-returns", "faqs"]
res.sort(key=lambda x: ORDER.index(x["slug"]) if x["slug"] in ORDER else 99)

HEAD = """\
################################################################################
  OTAKU STORE NG  —  STANDARD PAGES  (paste into each WordPress/Elementor page)
  Linked from the PAGES ▾ menu (see 02_MENUS_AND_PAGES.txt)
################################################################################

For each page below:
  - Create the page in WordPress (Pages > Add New) with the PAGE TITLE.
  - Paste the HTML BODY into the editor's Code/HTML view (or an Elementor HTML/Text
    widget). It uses clean semantic tags — no inline styles, so it inherits your theme.
  - Set the SEO TITLE and META DESCRIPTION in Yoast/Rank Math.

"""

report = []
blocks = [HEAD]
for p in res:
    c = p["content"]
    for k in ("title", "body_html", "seo_title", "meta_description"):
        if k in c: c[k] = fix_cur(c[k])
    if len(c.get("seo_title", "")) > 60:
        report.append(f"{c['slug']}: seo_title {len(c['seo_title'])}->60"); c["seo_title"] = trim(c["seo_title"], 60)
    if len(c.get("meta_description", "")) > 155:
        report.append(f"{c['slug']}: meta {len(c['meta_description'])}->155"); c["meta_description"] = trim(c["meta_description"], 155)
    blocks.append(f"""
================================================================================
 PAGE: {c['title']}
 Slug: /{c['slug']}
================================================================================
SEO TITLE ({len(c.get('seo_title',''))} chars): {c.get('seo_title','')}
META DESCRIPTION ({len(c.get('meta_description',''))} chars): {c.get('meta_description','')}

----- HTML BODY (paste into the page) -----
{c['body_html']}
----- END -----
""")

open(OUT, "w", encoding="utf-8").write("\n".join(blocks))
print("wrote", OUT, "with", len(res), "pages")
for r in report: print("  trim:", r)
if not report: print("  (no length trims needed)")
