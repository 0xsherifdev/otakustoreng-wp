#!/usr/bin/env python3
"""
Build a clean canonical catalog from the Bumpa products.csv export.
Outputs build/catalog.json — one record per PRODUCT with variants folded in.
No network. Safe to re-run.
"""
import csv, re, json, collections, os, html

CSV = os.path.join(os.path.dirname(__file__), "..", "products.csv")
OUT = os.path.join(os.path.dirname(__file__), "catalog.json")

# ---------- helpers ----------
def slugify(s):
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return re.sub(r"-+", "-", s).strip("-") or "item"

def images_of(p):
    out = []
    for field in (p["Main Image"], p["Additional Images"]):
        for u in field.split("|"):
            u = u.strip()
            if u.startswith("http") and u not in out:
                out.append(u)
    return out

# Map raw Collections tokens -> (product category, franchise) buckets.
# Franchise tokens vs product-type tokens.
FRANCHISE_TOKENS = {
    "naruto": "Naruto", "one peice": "One Piece", "one piece": "One Piece",
    "aot": "Attack on Titan", "demon slayer": "Demon Slayer", "bleach": "Bleach",
    "jujustu kaisen": "Jujutsu Kaisen", "jujutsu kaisen": "Jujutsu Kaisen",
}
TYPE_TOKENS = {
    "t-shirts": "T-Shirts", "stone wash t-shirt": "T-Shirts", "hoodies": "Hoodies",
    "anime jersey": "Jerseys", "kimono": "Kimono", "headwears": "Headwear",
    "trouser": "Trousers", "shorts": "Shorts", "shoes": "Shoes",
    "accessories": "Accessories", "chain": "Chains & Necklaces",
    "bracelet": "Bracelets", "rings": "Rings", "wallets": "Wallets",
    "landyard": "Lanyards", "anime figurines": "Figurines",
    "anime stickers": "Stickers", "anime katana": "Katana & Weapons",
    "anime bottle": "Bottles & Drinkware", "phone cases": "Phone Cases",
    "laptop skin": "Laptop Skins", "room decor": "Room Decor",
    "led frame lamp": "LED Lamps", "anime mask": "Masks", "anime tie": "Ties",
    "cosplays": "Cosplay", "couple accessories": "Couple Accessories",
    "air pod": "AirPods Cases", "totes bag": "Tote Bags",
}

def parse_collections(raw):
    cats, frs = [], []
    for tok in raw.split("|"):
        t = tok.strip().lower()
        if not t:
            continue
        if t in FRANCHISE_TOKENS:
            f = FRANCHISE_TOKENS[t]
            if f not in frs: frs.append(f)
        elif t in TYPE_TOKENS:
            c = TYPE_TOKENS[t]
            if c not in cats: cats.append(c)
    return cats, frs

# fallback type inference from title keywords
TITLE_TYPE = [
    (r"\bjersey\b", "Jerseys"), (r"\bhoodie", "Hoodies"),
    (r"\bt[- ]?shirt|\btee\b|tshirt", "T-Shirts"), (r"\bkimono\b", "Kimono"),
    (r"\bsweat", "Hoodies"), (r"\bcap\b|beanie|bucket hat|head ?warmer|durag|headwear", "Headwear"),
    (r"\btrouser|\bpant|joggers?\b|sweatpant", "Trousers"), (r"\bshort", "Shorts"),
    (r"\bshoe|sneaker|slides?\b|sandal", "Shoes"),
    (r"katana|sword|weapon|kunai|blade|nichirin", "Katana & Weapons"),
    (r"figurine|figure\b|statue|gk\b", "Figurines"),
    (r"sticker", "Stickers"), (r"\bmug\b|bottle|flask|tumbler|cup\b", "Bottles & Drinkware"),
    (r"chain|necklace|pendant|dog ?tag", "Chains & Necklaces"),
    (r"bracelet|bangle", "Bracelets"), (r"\bring\b|rings", "Rings"),
    (r"wallet|card ?holder", "Wallets"), (r"lanyard|landyard", "Lanyards"),
    (r"phone ?case|airpod|air ?pod", "Phone Cases"), (r"laptop ?skin", "Laptop Skins"),
    (r"lamp|led|night ?light|frame light", "LED Lamps"),
    (r"poster|tapestry|wall|pillow|bed ?spread|foot ?mat|rug|decor", "Room Decor"),
    (r"mask\b", "Masks"), (r"\btie\b", "Ties"), (r"earring|stud", "Accessories"),
    (r"tote|bag\b|backpack", "Tote Bags"), (r"cosplay", "Cosplay"),
    (r"glove", "Accessories"),
]
TITLE_FRANCHISE = [
    (r"naruto|sasuke|itachi|kakashi|akatsuki|uchiha|sharingan|gaara|madara|jiraiya|hokage|minato|obito|rasengan", "Naruto"),
    (r"luffy|zoro|one ?p[ei]+ce|nami|sanji|ace\b|sabo|gear ?5|gomu|sunny|nika|shanks|law\b", "One Piece"),
    (r"attack on titan|\baot\b|eren|levi|mikasa|titan|survey corps|scout regiment", "Attack on Titan"),
    (r"demon slayer|tanjiro|nezuko|rengoku|zenitsu|inosuke|tomioka|kimetsu|nichirin|giyu|akaza|muzan", "Demon Slayer"),
    (r"bleach|ichigo|zangetsu|getsuga|bankai|hollow|aizen|kenpachi|byakuya", "Bleach"),
    (r"jujutsu|jujustu|gojo|sukuna|itadori|megumi|nobara|domain expansion|\bjjk\b", "Jujutsu Kaisen"),
    (r"goku|vegeta|dragon ?ball|saiyan|kamehameha|gohan|frieza|\bdbz\b", "Dragon Ball"),
    (r"berserk|guts\b|griffith|dragon ?slayer", "Berserk"),
    (r"solo leveling|sung ?jin|jin ?woo|monarch", "Solo Leveling"),
    (r"deku|my hero|all might|bakugo|todoroki|\bmha\b", "My Hero Academia"),
    (r"chainsaw|denji|makima|pochita", "Chainsaw Man"),
    (r"tokyo revengers|mikey|draken|manjiro", "Tokyo Revengers"),
    (r"hunter|hxh|gon\b|killua|hisoka", "Hunter x Hunter"),
    (r"jojo|jotaro|dio\b|star platinum", "JoJo's Bizarre Adventure"),
]

def infer_from_title(title, cats, frs):
    low = title.lower()
    if not cats:
        for pat, c in TITLE_TYPE:
            if re.search(pat, low):
                cats = [c]; break
    if not frs:
        for pat, f in TITLE_FRANCHISE:
            if re.search(pat, low):
                frs = [f]; break
    return cats, frs

# ---------- build ----------
rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
by_pid = collections.defaultdict(list)
for r in rows:
    by_pid[r["Product ID"]].append(r)

catalog = []
slug_seen = collections.Counter()
for pid, group in by_pid.items():
    prod = next((r for r in group if r["Row Type"] == "product"), None)
    if not prod:
        continue
    variants = [r for r in group if r["Row Type"] == "variant"]
    title = prod["Title"].strip()
    base_slug = slugify(title)
    slug_seen[base_slug] += 1
    slug = base_slug if slug_seen[base_slug] == 1 else f"{base_slug}-{pid}"

    cats, frs = parse_collections(prod["Collections"])
    cats, frs = infer_from_title(title, cats, frs)

    # variant pricing/stock
    vlist = []
    prices = []
    for v in variants:
        try: price = float(v["Price"]) if v["Price"].strip() else None
        except: price = None
        try: stock = int(v["Stock"]) if v["Stock"].strip().lstrip("-").isdigit() else 0
        except: stock = 0
        if price: prices.append(price)
        vlist.append({"variant_id": v["Variant ID"], "name": v["Variant Name"].strip(),
                      "price": price, "stock": stock})
    # product-level price fallback
    if not prices:
        try:
            pp = float(prod["Price"]) if prod["Price"].strip() else None
            if pp: prices.append(pp)
        except: pass
    try: prod_stock = int(prod["Stock"]) if prod["Stock"].strip().lstrip("-").isdigit() else 0
    except: prod_stock = 0

    option_name = prod["Options Names"].strip()
    option_values_raw = prod["Options Values"].strip()
    try:
        option_values = json.loads(option_values_raw) if option_values_raw.startswith("[") else []
    except Exception:
        option_values = []

    desc = prod["Description"].strip()
    # strip simple html tags but keep text
    desc_text = html.unescape(re.sub(r"<[^>]+>", " ", desc)).strip()
    desc_text = re.sub(r"\s+", " ", desc_text)

    rec = {
        "product_id": pid,
        "title": title,
        "slug": slug,
        "categories": cats,
        "franchises": frs,
        "is_variable": len(vlist) > 0 and bool(option_name),
        "option_name": option_name,
        "option_values": option_values,
        "variants": vlist,
        "price_min": min(prices) if prices else None,
        "price_max": max(prices) if prices else None,
        "total_stock": sum(v["stock"] for v in vlist) if vlist else prod_stock,
        "featured": prod["Featured"].strip() == "1",
        "images": images_of(prod),
        "description_raw": desc,
        "description_text": desc_text,
        "created_at": prod["Created At"].strip(),
    }
    catalog.append(rec)

# sort by created desc-ish (keep stable by title)
catalog.sort(key=lambda r: (r["categories"][0] if r["categories"] else "zzz", r["title"]))
json.dump(catalog, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# summary
print("Products:", len(catalog))
print("Variable:", sum(1 for r in catalog if r["is_variable"]))
print("With images:", sum(1 for r in catalog if r["images"]))
print("Total images:", sum(len(r["images"]) for r in catalog))
print("No category:", sum(1 for r in catalog if not r["categories"]))
print("No franchise:", sum(1 for r in catalog if not r["franchises"]))
print("No description:", sum(1 for r in catalog if not r["description_text"]))
catc = collections.Counter()
for r in catalog:
    for c in (r["categories"] or ["(uncategorized)"]):
        catc[c]+=1
print("\n=== CLEAN CATEGORIES ===")
for k,v in catc.most_common(): print(f"  {v:4d}  {k}")
frc = collections.Counter()
for r in catalog:
    for f in (r["franchises"] or ["(none)"]):
        frc[f]+=1
print("\n=== CLEAN FRANCHISES ===")
for k,v in frc.most_common(): print(f"  {v:4d}  {k}")
