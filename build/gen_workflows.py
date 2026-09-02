#!/usr/bin/env python3
"""Inject catalog data + brand context into the JS workflow templates."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
catalog = json.load(open(os.path.join(HERE, "catalog.json"), encoding="utf-8"))

# ---------------- shared brand context ----------------
BRAND = "Otaku Store NG"
TAGLINE_RULE = ("Brand tagline must NOT reference Nigeria. It should be about anime fandom, "
                "gear, power, or wearing your favourite series. Short and ownable.")
STYLE = ("DARK MANGA aesthetic. Palette: ink black #111111, paper white #FAFAFA, and a single "
         "bold manga-red #E2261C accent (use sparingly for energy). Textures: halftone/screentone "
         "dots, manga speed lines, brush-ink splatter, manga panel layouts, high contrast monochrome "
         "with one red pop. Mood: premium anime-streetwear, bold, cinematic.")
MARKET = ("Based in Nigeria, ships nationwide AND internationally/worldwide. Prices in Nigerian Naira (₦). "
          "Trust signals: secure checkout, fast nationwide + worldwide delivery, easy returns. "
          "Do NOT make the brand identity Nigeria-only — it's a global anime brand that happens to ship from Nigeria.")
PRICE_FACTS = ("Anime jerseys ₦23,000. Catalog ranges ₦1,000 (stickers/small accessories) to ₦250,000 "
               "(premium katana/figurines), median ~₦18,500. Free-shipping threshold and promos should feel realistic.")

# ---------------- category tree (canonical WooCommerce taxonomy) ----------------
CATEGORY_TREE = {
    "Apparel": ["Jerseys", "T-Shirts", "Hoodies", "Kimono", "Trousers", "Shorts", "Headwear", "Shoes", "Ties", "Cosplay"],
    "Accessories": ["Chains & Necklaces", "Bracelets", "Rings", "Wallets", "Lanyards",
                     "Phone Cases", "AirPods Cases", "Laptop Skins", "Masks", "Tote Bags", "Couple Accessories"],
    "Collectibles": ["Figurines", "Katana & Weapons", "Stickers", "Bottles & Drinkware"],
    "Home & Decor": ["Room Decor", "LED Lamps"],
    "Shop by Anime": ["Naruto", "One Piece", "Attack on Titan", "Demon Slayer", "Bleach",
                       "Jujutsu Kaisen", "Dragon Ball", "Hunter x Hunter", "Berserk",
                       "Solo Leveling", "Chainsaw Man", "My Hero Academia", "Tokyo Revengers"],
}

HERO_PRODUCTS = [
    {"type": "Anime Jerseys", "example": "Gojo / Itachi / Luffy all-over-print jerseys", "price": "₦23,000", "note": "signature product, vivid full-print"},
    {"type": "Hoodies", "example": "Sukuna, Kaneki, Gojo hoodies", "note": "97 styles, streetwear staple"},
    {"type": "Katana & Weapons", "example": "Tanjiro Nichirin blade, Zoro / Yubashiri katana", "note": "premium collectible display pieces"},
    {"type": "Figurines", "example": "anime GK figures & statues", "note": "collector shelf pieces"},
    {"type": "Chains & Necklaces", "example": "Akatsuki cloud, Uchiha, dog-tag chains", "note": "139 accessories, entry-price hype items"},
    {"type": "Kimono", "example": "haori / kimono robes", "note": "statement layering pieces"},
]

SECTION_MAP = """\
You are mapping content onto the Minimog (Fashion demo) homepage. Fill EVERY numbered slot.

1. ANNOUNCEMENT BAR (rotating, short) — 2-3 rotating messages (e.g. shipping, new drops, app).
2. HEADER — logo wordmark idea, primary nav menu items (Home, Shop, New In, Anime, Blog, Track Order, Contact), search placeholder text, and the left "SHOP BY CATEGORIES" mega-menu (list the category tree).
3. HERO SLIDER — 2 slides. Each: eyebrow, big headline, 1-line subtext, CTA button label, target. + IMAGE PROMPT for each slide.
4. THREE PROMO BANNER CARDS (small grid under hero) — 3 cards, each: title, 1-line, CTA. + IMAGE PROMPT each.
5. POPULAR CATEGORIES (icon row) — 7 category chips with label (pick best-sellers) + one IMAGE PROMPT describing the icon style for the whole row.
6. TRENDING COLLECTION (3 large cards) — 3 cards: title + subtext. + IMAGE PROMPT each.
7. WHAT'S TRENDING THIS WEEK (feature block) — a left feature panel (badge, headline, paragraph, CTA) + 2 product spotlight cards (name + price). + IMAGE PROMPT for the feature panel.
8. FEATURED PRODUCTS (tabbed grid) — tab labels (by category/anime) + intro line. (Products auto-pull; just give the heading + tabs + a SALE-badge note.)
9. PROMO / DEAL BAR — headline, deal line with ₦ price (strike + now), CTA. + IMAGE PROMPT background.
10. SERVICE ICONS ROW — 4 trust badges, each: title + 1-line (shipping NG + worldwide, guarantee, support, secure payment).
11. FOOTER — brand blurb (2 lines), 4 link columns (FIND IT FAST / CUSTOMER CARE / SHOP / COMPANY) with realistic links, newsletter heading + subtext + button label + consent microcopy, social handles line, payment methods line, copyright line.
12. SEO / META — homepage <title> (<=60 chars) + meta description (<=155 chars).
13. BRAND BONUS — final chosen tagline + 3 alternate taglines + a 2-3 sentence "brand voice guide" the user can reuse."""

OUTPUT_RULES = """\
- Output PLAIN TEXT (no markdown tables). Use clear section headers exactly like "## SECTION 3 — HERO SLIDER".
- For every line of copy that replaces template text, prefix with "REPLACE WITH:" so it is obvious what to paste.
- For every visual, add a line "IMAGE PROMPT (Google Flow): <full prompt>" including palette, texture, composition, aspect ratio (e.g. 16:9 hero, 1:1 cards, 3:4 promo), and "no text overlay, no watermark".
- Keep it tight and skimmable. Real, paste-ready copy — not placeholders.
- Use ₦ for all prices."""

CTX = {
    "brand": BRAND, "taglineRule": TAGLINE_RULE, "style": STYLE, "market": MARKET,
    "priceFacts": PRICE_FACTS, "categoryTree": CATEGORY_TREE, "heroProducts": HERO_PRODUCTS,
    "sectionMap": SECTION_MAP, "outputRules": OUTPUT_RULES,
}

# ---------------- jerseys subset ----------------
jerseys = [r for r in catalog if "Jerseys" in r["categories"]]
# trim to fields the agent needs
jslim = [{
    "title": j["title"], "slug": j["slug"], "product_id": j["product_id"],
    "franchises": j["franchises"],
    "variants": [{"name": v["name"], "price": v["price"], "stock": v["stock"]} for v in j["variants"]],
    "price_min": j["price_min"], "images": j["images"],
    "description_text": j["description_text"],
} for j in jerseys]

JERSEY_KNOWLEDGE = ("An 'anime jersey' here is an ALL-OVER-PRINT (dye-sublimated) jersey: vivid edge-to-edge "
    "graphics featuring a character or manga-panel collage. Lightweight, breathable 100% polyester. "
    "Common cuts: button-up baseball jersey and basketball/American-football style. Unisex fit, true to size "
    "(if between sizes, advise sizing up). Machine wash cold inside-out, do not iron the print directly. "
    "Great for conventions, match-watch parties, streetwear layering. Describe these truthfully; do not invent "
    "exact GSM weights or fake certifications.")

STYLE_OBJ = {
    "brand": BRAND,
    "text": (f"BRAND: {BRAND}. {TAGLINE_RULE}\nVISUAL STYLE for image prompts: {STYLE}\nMARKET: {MARKET}\n"
             "VOICE: energetic, knowledgeable anime-fan voice; speak to fans; confident but not cringe; "
             "max 1 emoji only if it helps. Currency ₦ (Naira). Never claim official/licensed."),
    "jerseyKnowledge": JERSEY_KNOWLEDGE,
}

# ---------------- inject ----------------
def inject(tpl_name, out_name, repls):
    src = open(os.path.join(HERE, tpl_name), encoding="utf-8").read()
    for token, val in repls.items():
        src = src.replace(token, json.dumps(val, ensure_ascii=False))
    open(os.path.join(HERE, out_name), "w", encoding="utf-8").write(src)
    print("wrote", out_name, f"({len(src)} bytes)")

inject("tpl_homepage.js", "wf_homepage.js", {"/*CTX_JSON*/": CTX})
inject("tpl_jerseys.js", "wf_jerseys.js", {"/*JERSEYS_JSON*/": jslim, "/*STYLE_JSON*/": STYLE_OBJ})

# save data for transparency
json.dump(jslim, open(os.path.join(HERE, "jerseys.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
json.dump(CTX, open(os.path.join(HERE, "homepage_ctx.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("jerseys:", len(jslim))
