#!/usr/bin/env python3
"""
Generate category-aware product-content workflow batches for ALL remaining
products (everything except the already-done jerseys pilot).

Splits into batches of <= MAX_PER_BATCH products so each workflow stays well
under the 1000-agent cap (write+verify = 2 agents/product). Writes
build/wf_products_batchNN.js for each batch.
"""
import json, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
from render_products import attr_name, attr_value  # reuse the canonical logic

MAX_PER_BATCH = 100   # smaller batches to stay under the rolling rate limit

catalog = json.load(open(os.path.join(HERE, "catalog.json"), encoding="utf-8"))
done = set(j["slug"] for j in json.load(open(os.path.join(HERE, "jerseys_content.json"), encoding="utf-8")))
# also skip any products already completed in a previous product run (accumulator)
_done_path = os.path.join(HERE, "products_done.json")
if os.path.exists(_done_path):
    done |= set(j["slug"] for j in json.load(open(_done_path, encoding="utf-8")))
remaining = [r for r in catalog if r["slug"] not in done]

# ---------------- brand/style ----------------
BRAND = "Otaku Store NG"
STYLE_OBJ = {
    "brand": BRAND,
    "text": (f"BRAND: {BRAND}. Tagline 'Wear the roster.' Brand taglines/voice are NOT about Nigeria.\n"
             "VISUAL STYLE for image prompts: DARK MANGA — ink black #111111, paper white #FAFAFA, single "
             "manga-red #E2261C accent; halftone dots, speed lines, ink splatter, manga panels; premium, cinematic.\n"
             "MARKET: ships from Nigeria, nationwide + worldwide; prices in Naira (₦).\n"
             "VOICE: energetic, knowledgeable anime-fan voice; speak to fans; confident, premium, never cringe; "
             "max 1 emoji only if it truly helps. Never claim official/licensed (fan / anime-inspired, not affiliated)."),
}

# ---------------- category knowledge (accurate, compliance-aware) ----------------
GENERIC = ("Anime-inspired fan merchandise. Describe truthfully and benefit-led for a fan audience; "
           "do not invent exact measurements, weights, or certifications.")
KNOWLEDGE = {
 "Jerseys": "All-over-print (dye-sublimated) jersey: vivid edge-to-edge graphics on lightweight breathable 100% polyester; baseball/American-football cut; unisex, true to size (size up if between); machine wash cold inside-out, no direct ironing on the print.",
 "T-Shirts": "Anime graphic or all-over-print t-shirt; soft cotton or cotton/polyester blend (all-over-print versions are polyester); unisex regular fit; crew neck; durable fade-resistant print; machine wash cold inside-out. Some are stone-wash/acid-wash tees with a vintage faded finish.",
 "Hoodies": "Anime graphic / all-over-print pullover or zip-up hoodie; brushed-fleece interior for warmth; ribbed cuffs and hem; kangaroo pocket (pullover); unisex streetwear fit; some come in a choice of fabric (e.g. thick cotton vs thick polyester); machine wash cold inside-out.",
 "Kimono": "Anime-printed haori / kimono robe; lightweight open-front layering piece with wide sleeves; unisex free-size drape; great as a statement layer over a tee; gentle wash, hang dry.",
 "Trousers": "Anime-print or embroidered trousers — joggers, cargos or sweatpants; comfortable elastic/drawstring waist; unisex; pair with the matching jersey or hoodie.",
 "Shorts": "Anime-print shorts; lightweight, breathable; elastic drawstring waist; unisex; great for warm weather and casual fits.",
 "Headwear": "Anime headwear — could be a snapback/dad cap, beanie, bucket hat, durag or knitted head-warmer; one-size adjustable where applicable; embroidered or printed motif.",
 "Shoes": "Anime-print footwear — sneakers, canvas shoes or slides with all-over character art; cushioned sole; true to size; unisex. State that buyers pick their shoe size.",
 "Ties": "Anime-print necktie; smooth woven finish; standard adult length; a subtle way to rep your series at work or events.",
 "Cosplay": "Anime cosplay costume / outfit set; pieces as shown for the character; polyester construction; check the size option before ordering; for conventions, shoots and events.",
 "Chains & Necklaces": "Anime-inspired pendant necklace / chain (incl. dog-tag styles); durable stainless-steel or alloy that resists tarnish; adjustable/standard chain length; comes in a choice of designs where offered; wipe clean.",
 "Bracelets": "Anime-inspired bracelet — stainless-steel, beaded, cord or cuff style depending on the design; adjustable or standard fit; everyday-durable.",
 "Rings": "Anime-inspired ring in stainless steel / alloy; available in standard ring sizes (buyer selects size); polished finish; tarnish-resistant for daily wear.",
 "Wallets": "Anime-print wallet or card holder; PU leather or canvas; multiple card slots and a note compartment; slim everyday carry; printed character artwork.",
 "Lanyards": "Anime-print lanyard for keys, ID or badge; woven polyester strap with a metal clip; lightweight everyday accessory.",
 "Phone Cases": "Anime-print phone case; slim protective shell (TPU/hard PC); raised edges to protect the screen; precise cutouts; buyer selects their phone model/design where offered.",
 "AirPods Cases": "Anime-print AirPods case; shock-absorbing cover with precise port cutout; clips to a bag or keyring; buyer selects the AirPods model/design.",
 "Laptop Skins": "Anime laptop skin — a printed vinyl decal/wrap; bubble-free application, residue-free removal; buyer selects size/model; refreshes your laptop with character art.",
 "Masks": "Anime mask — a cosplay/display face mask (e.g. ANBU-style or character mask) or a printed fabric mask depending on the design; for cosplay, costume and fan display.",
 "Tote Bags": "Anime-print tote bag; sturdy canvas with reinforced handles; roomy everyday carry for books, groceries or con hauls; printed character artwork.",
 "Couple Accessories": "Matching anime couple set (e.g. paired rings, chains or bracelets); sold as a his-and-hers / duo set; great gift for fans; durable everyday materials.",
 "Figurines": "Anime collector figurine / statue — detailed sculpted PVC/resin display piece; pre-painted; for shelf display (not a toy); handle with care; sizes vary by figure.",
 "Katana & Weapons": "Anime display katana / replica weapon — a DECORATIVE collector and cosplay display piece, typically with a stainless or alloy blade, themed handle wrap (tsuka) and scabbard (saya), often with a stand. Sold for display, cosplay and collecting; describe as a display/collectible prop, never as a weapon for harm. Keep away from children; follow local laws on bladed display items.",
 "Stickers": "Anime vinyl sticker / sticker pack; waterproof and durable; sticks to laptops, water bottles, phones, notebooks; vivid fade-resistant print; buyer picks the design/number where offered.",
 "Bottles & Drinkware": "Anime drinkware — water bottle, flask, tumbler or mug with character artwork; food-safe materials; check capacity option; hand-wash recommended to protect the print.",
 "Room Decor": "Anime room decor — could be a poster, wall tapestry, throw pillow/cushion cover, bed spread, foot mat/rug or wall art depending on the design; vivid print; transforms an otaku space. Sizes/sets vary by item.",
 "LED Lamps": "Anime LED lamp — an acrylic 3D illusion / frame night light; USB-powered; energy-efficient LEDs; many offer multiple light colours; a centrepiece for a fan's desk or shelf. Buyer picks the design where offered.",
 "Accessories": "Anime-inspired accessory — depending on the design this may be a keychain, badge, pin, earring, dog-tag, brooch or similar small item. Durable everyday materials (often stainless steel/alloy/enamel). Read the title and options for the exact item and describe it accurately as an affordable way for a fan to rep their series.",
}

# generic catch-all buckets we'd rather replace with a more specific sub-category
GENERIC_CATS = {"Accessories"}

def primary_category(rec):
    cats = rec["categories"]
    if not cats:
        return "Anime Merch"
    specific = [c for c in cats if c not in GENERIC_CATS]
    return specific[0] if specific else cats[0]

# ---------------- build slim product records ----------------
def slim(rec):
    cat = primary_category(rec)
    an = attr_name(rec.get("option_name"), [v["name"] for v in rec["variants"]])
    vals = []
    seen = set()
    for v in rec["variants"]:
        s = attr_value(an, v["name"])
        if s and s not in seen:
            seen.add(s); vals.append(s)
    return {
        "title": rec["title"], "slug": rec["slug"], "product_id": rec["product_id"],
        "franchises": rec["franchises"], "category": cat,
        "all_categories": rec["categories"],
        "knowledge": KNOWLEDGE.get(cat, GENERIC),
        "attr_name": an if rec.get("option_name") and rec["variants"] else "",
        "option_values": vals if rec.get("option_name") else [],
        "price_min": rec.get("price_min") or 0,
        "n_images": len(rec["images"]),
        "description_text": rec["description_text"][:300],
    }

products = [slim(r) for r in remaining]
# group by category so batches are coherent (better cache + thematic runs)
products.sort(key=lambda p: (p["category"], p["title"]))

n_batches = math.ceil(len(products) / MAX_PER_BATCH)
tpl = open(os.path.join(HERE, "tpl_products.js"), encoding="utf-8").read()
manifest = []
for i in range(n_batches):
    chunk = products[i * MAX_PER_BATCH:(i + 1) * MAX_PER_BATCH]
    src = tpl.replace("/*PRODUCTS_JSON*/", json.dumps(chunk, ensure_ascii=False))
    src = src.replace("/*STYLE_JSON*/", json.dumps(STYLE_OBJ, ensure_ascii=False))
    out = f"wf_products_batch{i+1:02d}.js"
    open(os.path.join(HERE, out), "w", encoding="utf-8").write(src)
    manifest.append({"file": out, "count": len(chunk), "agents": len(chunk) * 2})
    print(f"wrote {out}: {len(chunk)} products ({len(chunk)*2} agents)")

json.dump(manifest, open(os.path.join(HERE, "product_batches.json"), "w"), indent=2)
print(f"\nTOTAL: {len(products)} products in {n_batches} batches")
import collections
cc = collections.Counter(p["category"] for p in products)
print("categories with no knowledge snippet (using GENERIC):",
      sorted(set(p["category"] for p in products) - set(KNOWLEDGE) ))
