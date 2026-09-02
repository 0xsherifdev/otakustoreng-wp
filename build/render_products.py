#!/usr/bin/env python3
"""
Merge AI-generated content (from a workflow output JSON) with the canonical
catalog (prices/stock/variants/images) to produce, per product:
  - products/<slug>/info.txt        (human-readable WooCommerce product sheet)
and a single native WooCommerce Product CSV importer file for the batch.

Usage:
  python3 render_products.py --content build/jerseys_content.json \
                             --csv build/woocommerce_jerseys_import.csv \
                             --label "Jerseys pilot"

The --content JSON is the array returned by the jerseys/products workflow:
  [ { "slug","product_id","content": {franchise,character,subtitle,
       short_description,long_description_html,highlights[],seo_title,
       meta_description,focus_keyword,tags[],image_alt,
       supplemental_image_prompt}, "issues":[...] }, ... ]
"""
import json, os, csv, argparse, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CATALOG = json.load(open(os.path.join(HERE, "catalog.json"), encoding="utf-8"))
CAT_BY_SLUG = {r["slug"]: r for r in CATALOG}

# child category -> parent (canonical taxonomy)
CATEGORY_TREE = {
    "Apparel": ["Jerseys", "T-Shirts", "Hoodies", "Kimono", "Trousers", "Shorts", "Headwear", "Shoes", "Ties", "Cosplay"],
    "Accessories": ["Chains & Necklaces", "Bracelets", "Rings", "Wallets", "Lanyards",
                     "Phone Cases", "AirPods Cases", "Laptop Skins", "Masks", "Tote Bags", "Couple Accessories"],
    "Collectibles": ["Figurines", "Katana & Weapons", "Stickers", "Bottles & Drinkware"],
    "Home & Decor": ["Room Decor", "LED Lamps"],
}
CHILD_PARENT = {c: p for p, kids in CATEGORY_TREE.items() for c in kids}
FRANCHISES = {"Naruto", "One Piece", "Attack on Titan", "Demon Slayer", "Bleach", "Jujutsu Kaisen",
              "Dragon Ball", "Hunter x Hunter", "Berserk", "Solo Leveling", "Chainsaw Man",
              "My Hero Academia", "Tokyo Revengers", "JoJo's Bizarre Adventure", "Blue Lock",
              "Naruto Shippuden", "Bleach: Thousand-Year Blood War"}

SIZE_MAP = {"m": "M", "l": "L", "xl": "XL", "xxl": "2XL", "2xl": "2XL", "3xl": "3XL",
            "4xl": "4XL", "s": "S", "xs": "XS"}

def norm_size(name):
    k = name.strip().lower()
    return SIZE_MAP.get(k, name.strip().upper() if len(name.strip()) <= 4 else name.strip())

def naira(n):
    if n is None:
        return ""
    return f"₦{int(round(n)):,}"

def money(n):
    if n is None or n == "":
        return ""
    f = float(n)
    return str(int(f)) if f == int(f) else f"{f:.2f}"

SIZE_TOKENS = {"xs", "s", "m", "l", "xl", "xxl", "xxxl", "2xl", "3xl", "4xl", "5xl"}

def _looks_like_size(values):
    if not values: return False
    hits = sum(1 for v in values if v.strip().lower() in SIZE_TOKENS)
    return hits >= max(1, len(values) * 0.6)

def _map_token(t):
    if "size" in t: return "Size"
    if "material" in t: return "Material"
    if "colo" in t: return "Color"
    return "Style"

def attr_name(option_name, variant_names=None):
    """Map to a WooCommerce attribute name. Detects 'Size' from the actual
    variant VALUES first (Bumpa option names are unreliable, e.g. 'm')."""
    toks = [t.strip().lower() for t in (option_name or "").split("|") if t.strip()]
    if len(toks) > 1:  # combined attribute, e.g. sizes|material -> "Size & Material"
        mapped = []
        for t in toks:
            m = _map_token(t)
            if m not in mapped: mapped.append(m)
        return " & ".join(mapped)
    if _looks_like_size(variant_names or []):
        return "Size"
    return _map_token(toks[0]) if toks else "Style"

def attr_value(attr, raw):
    """Normalise a variant value (only uppercase pure sizes)."""
    return norm_size(raw) if attr == "Size" else raw.strip()

def sku_for(pid, suffix=None):
    base = f"OSN-{pid}"
    if suffix:
        s = re.sub(r"[^A-Za-z0-9]+", "", str(suffix)).upper()
        return f"{base}-{s}"
    return base

def wc_categories(rec, content):
    cats = []
    for c in rec["categories"]:
        parent = CHILD_PARENT.get(c)
        cats.append(f"{parent} > {c}" if parent else c)
    # franchise -> Shop by Anime
    fr = content.get("franchise", "").strip()
    franchises = list(rec["franchises"])
    if fr and fr in FRANCHISES and fr not in franchises:
        franchises.append(fr)
    for f in franchises:
        if f in FRANCHISES:
            cats.append(f"Shop by Anime > {f}")
    # dedupe preserve order
    seen, out = set(), []
    for c in cats:
        if c not in seen:
            seen.add(c); out.append(c)
    return out or ["Uncategorized"]

# WooCommerce native importer columns
COLUMNS = ["Type", "SKU", "Name", "Published", "Is featured?", "Visibility in catalog",
           "Short description", "Description", "Tax status", "In stock?", "Stock",
           "Backorders allowed?", "Sold individually?", "Weight (kg)",
           "Allow customer reviews?", "Sale price", "Regular price", "Categories", "Tags",
           "Images", "Parent", "Position",
           "Attribute 1 name", "Attribute 1 value(s)", "Attribute 1 visible",
           "Attribute 1 global", "Attribute 1 default",
           "Meta: _yoast_wpseo_title", "Meta: _yoast_wpseo_metadesc", "Meta: _yoast_wpseo_focuskw"]


def build_rows(rec, content):
    """Return list of CSV row dicts (parent + variation rows) for one product."""
    pid = rec["product_id"]
    variants = rec["variants"]
    has_var = bool(variants) and bool(rec.get("option_name"))
    attr = attr_name(rec.get("option_name"), [v["name"] for v in variants])
    sizes = []
    seen = set()
    for v in variants:
        s = attr_value(attr, v["name"])
        if s and s not in seen:
            seen.add(s); sizes.append(s)
    cats = ", ".join(wc_categories(rec, content))
    tags = ", ".join(content.get("tags", []))
    images = ", ".join(rec["images"])  # WooCommerce sideloads remote URLs (main first = featured)
    price = rec.get("price_min") or 23000
    feat = 1 if rec.get("featured") else 0

    rows = []
    if has_var and sizes:
        # parent variable row
        rows.append({
            "Type": "variable", "SKU": sku_for(pid), "Name": rec["title"], "Published": 1,
            "Is featured?": feat, "Visibility in catalog": "visible",
            "Short description": content.get("short_description", ""),
            "Description": content.get("long_description_html", ""),
            "Tax status": "taxable", "In stock?": 1 if rec["total_stock"] > 0 else 0,
            "Stock": rec["total_stock"], "Backorders allowed?": 0, "Sold individually?": 0,
            "Weight (kg)": "", "Allow customer reviews?": 1, "Sale price": "",
            "Regular price": "", "Categories": cats, "Tags": tags, "Images": images,
            "Parent": "", "Position": 0,
            "Attribute 1 name": attr, "Attribute 1 value(s)": ", ".join(sizes),
            "Attribute 1 visible": 1, "Attribute 1 global": 1,
            "Attribute 1 default": sizes[0],
            "Meta: _yoast_wpseo_title": content.get("seo_title", ""),
            "Meta: _yoast_wpseo_metadesc": content.get("meta_description", ""),
            "Meta: _yoast_wpseo_focuskw": content.get("focus_keyword", ""),
        })
        for i, v in enumerate(variants):
            s = attr_value(attr, v["name"])
            rows.append({
                "Type": "variation", "SKU": sku_for(pid, s),
                "Name": f"{rec['title']} - {s}", "Published": 1, "Is featured?": 0,
                "Visibility in catalog": "visible", "Short description": "", "Description": "",
                "Tax status": "taxable", "In stock?": 1 if v["stock"] > 0 else 0,
                "Stock": v["stock"], "Backorders allowed?": 0, "Sold individually?": 0,
                "Weight (kg)": "", "Allow customer reviews?": 0, "Sale price": "",
                "Regular price": money(v["price"] or price), "Categories": "", "Tags": "",
                "Images": "", "Parent": sku_for(pid), "Position": i + 1,
                "Attribute 1 name": attr, "Attribute 1 value(s)": s,
                "Attribute 1 visible": 1, "Attribute 1 global": 1, "Attribute 1 default": "",
                "Meta: _yoast_wpseo_title": "", "Meta: _yoast_wpseo_metadesc": "",
                "Meta: _yoast_wpseo_focuskw": "",
            })
    else:
        # simple product
        rows.append({
            "Type": "simple", "SKU": sku_for(pid), "Name": rec["title"], "Published": 1,
            "Is featured?": feat, "Visibility in catalog": "visible",
            "Short description": content.get("short_description", ""),
            "Description": content.get("long_description_html", ""),
            "Tax status": "taxable", "In stock?": 1 if rec["total_stock"] > 0 else 0,
            "Stock": rec["total_stock"], "Backorders allowed?": 0, "Sold individually?": 0,
            "Weight (kg)": "", "Allow customer reviews?": 1, "Sale price": "",
            "Regular price": money(price), "Categories": cats, "Tags": tags, "Images": images,
            "Parent": "", "Position": 0,
            "Attribute 1 name": "", "Attribute 1 value(s)": "", "Attribute 1 visible": "",
            "Attribute 1 global": "", "Attribute 1 default": "",
            "Meta: _yoast_wpseo_title": content.get("seo_title", ""),
            "Meta: _yoast_wpseo_metadesc": content.get("meta_description", ""),
            "Meta: _yoast_wpseo_focuskw": content.get("focus_keyword", ""),
        })
    return rows, sizes, has_var


INFO_TMPL = """\
================================================================================
 OTAKU STORE NG — PRODUCT SHEET
================================================================================
PRODUCT NAME : {title}
SLUG         : {slug}
BUMPA ID     : {pid}
WOO TYPE     : {wtype}
PARENT SKU   : {sku}

--------------------------------------------------------------------------------
 CATEGORIES (WooCommerce)
--------------------------------------------------------------------------------
{cats}

TAGS: {tags}
FRANCHISE: {franchise}    CHARACTER: {character}

--------------------------------------------------------------------------------
 PRICING (NGN)  &  STOCK
--------------------------------------------------------------------------------
Regular price : {price}
Total stock   : {stock}
{variations_block}
--------------------------------------------------------------------------------
 SUBTITLE / HOOK
--------------------------------------------------------------------------------
{subtitle}

--------------------------------------------------------------------------------
 SHORT DESCRIPTION  (WooCommerce excerpt)
--------------------------------------------------------------------------------
{short_desc}

--------------------------------------------------------------------------------
 LONG DESCRIPTION  (WooCommerce description — HTML, paste into the editor's Text/HTML tab)
--------------------------------------------------------------------------------
{long_desc}

--------------------------------------------------------------------------------
 PRODUCT HIGHLIGHTS
--------------------------------------------------------------------------------
{highlights}

--------------------------------------------------------------------------------
 SEO  (Yoast / Rank Math)
--------------------------------------------------------------------------------
SEO Title ({seo_len} chars)        : {seo_title}
Meta Description ({meta_len} chars) : {meta_desc}
Focus keyword                       : {focus_kw}

--------------------------------------------------------------------------------
 IMAGES IN THIS FOLDER
--------------------------------------------------------------------------------
{images_block}
PRIMARY IMAGE ALT TEXT: {image_alt}

GOOGLE FLOW IMAGE PROMPT (optional supplemental lifestyle/studio shot):
{supp_prompt}

--------------------------------------------------------------------------------
 NOTES / DATA FLAGS
--------------------------------------------------------------------------------
{notes}
================================================================================
"""


def render_info(rec, content, rows, sizes, has_var, issues):
    folder = os.path.join(ROOT, "products", rec["slug"])
    cats = "\n".join("  - " + c for c in wc_categories(rec, content))
    if has_var and sizes:
        attr = attr_name(rec.get("option_name"), [v["name"] for v in rec["variants"]])
        vb_lines = [f"VARIATIONS (attribute: {attr})"]
        for v in rec["variants"]:
            s = attr_value(attr, v["name"])
            vb_lines.append(f"  {s:<14} | {naira(v['price'] or rec.get('price_min'))} | stock {v['stock']:<4} | SKU {sku_for(rec['product_id'], s)}")
        variations_block = "\n".join(vb_lines) + "\n"
    else:
        variations_block = "(simple product — no size variations)\n"
    # images present in folder
    imgs = []
    for i, url in enumerate(rec["images"], 1):
        ext = url.split("?")[0].rsplit(".", 1)[-1].lower()
        ext = "jpg" if ext == "jpeg" else ext
        fname = f"{i:02d}.{ext}"
        present = os.path.exists(os.path.join(folder, fname))
        tag = "" if present else "   [MISSING — dead source URL, generate replacement]"
        role = "primary/featured" if i == 1 else "gallery"
        imgs.append(f"  {fname}  ({role}){tag}")
    images_block = "\n".join(imgs) if imgs else "  (no images)"
    hl = "\n".join("  • " + h for h in content.get("highlights", []))
    notes = []
    if not CAT_BY_SLUG[rec["slug"]]["description_text"]:
        notes.append("Original Bumpa description was empty/placeholder — copy written fresh.")
    if issues:
        notes.append("QA fixes applied: " + "; ".join(issues))
    if not rec["images"] or any(not os.path.exists(os.path.join(folder, f"{i:02d}." + ("jpg" if rec['images'][i-1].split('?')[0].rsplit('.',1)[-1].lower()=='jpeg' else rec['images'][i-1].split('?')[0].rsplit('.',1)[-1].lower()))) for i in range(1, len(rec['images'])+1)):
        pass
    if not notes:
        notes.append("No data flags.")
    seo_t = content.get("seo_title", "")
    meta_d = content.get("meta_description", "")
    txt = INFO_TMPL.format(
        title=rec["title"], slug=rec["slug"], pid=rec["product_id"],
        wtype=("variable" if (has_var and sizes) else "simple"), sku=sku_for(rec["product_id"]),
        cats=cats, tags=", ".join(content.get("tags", [])),
        franchise=content.get("franchise", "") or "(none)",
        character=content.get("character", "") or "(none)",
        price=naira(rec.get("price_min") or 23000), stock=rec["total_stock"],
        variations_block=variations_block, subtitle=content.get("subtitle", ""),
        short_desc=content.get("short_description", ""),
        long_desc=content.get("long_description_html", ""),
        highlights=hl, seo_title=seo_t, seo_len=len(seo_t),
        meta_desc=meta_d, meta_len=len(meta_d),
        focus_kw=content.get("focus_keyword", ""), images_block=images_block,
        image_alt=content.get("image_alt", ""),
        supp_prompt=content.get("supplemental_image_prompt", ""),
        notes="\n".join("  - " + n for n in notes),
    )
    open(os.path.join(folder, "info.txt"), "w", encoding="utf-8").write(txt)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--content", required=True)
    ap.add_argument("--csv", required=True)
    ap.add_argument("--label", default="batch")
    args = ap.parse_args()

    content_list = json.load(open(args.content, encoding="utf-8"))
    all_rows = []
    n_info = 0
    seo_warn = []
    for item in content_list:
        slug = item["slug"]
        rec = CAT_BY_SLUG.get(slug)
        if not rec:
            print("WARN: slug not in catalog:", slug); continue
        content = item["content"]
        rows, sizes, has_var = build_rows(rec, content)
        all_rows.extend(rows)
        render_info(rec, content, rows, sizes, has_var, item.get("issues", []))
        n_info += 1
        if len(content.get("seo_title", "")) > 60:
            seo_warn.append(f"{slug}: SEO title {len(content['seo_title'])} chars")
        if len(content.get("meta_description", "")) > 155:
            seo_warn.append(f"{slug}: meta {len(content['meta_description'])} chars")

    with open(args.csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        for r in all_rows:
            w.writerow(r)

    print(f"[{args.label}] info.txt written: {n_info}")
    print(f"[{args.label}] CSV rows: {len(all_rows)} -> {args.csv}")
    if seo_warn:
        print("SEO LENGTH WARNINGS:")
        for s in seo_warn:
            print("  -", s)
    else:
        print("All SEO titles <=60 and meta <=155.")


if __name__ == "__main__":
    main()
