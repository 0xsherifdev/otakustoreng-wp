################################################################################
  OTAKU STORE NG  —  TRANSFORMATION DELIVERABLES  (read me first)
  Bumpa  ->  WordPress + Minimog + WooCommerce   |   "Wear the roster."
################################################################################

WHAT YOU HAVE NOW
=================
A) WEBSITE CONTENT  (folder: content/)
   00_README_DELIVERABLES.txt .. this file
   01_HOMEPAGE.txt ............. homepage, section-by-section, matched to your live
                                 Minimog template (single hero + 4 mega-menus) with
                                 paste-ready Google Flow image prompts (Dark Manga).
   02_MENUS_AND_PAGES.txt ...... SHOP ▾ / PAGES ▾ dropdowns + the All Collections page
                                 (18 collection cards + image prompts).
   03_STANDARD_PAGES.txt ....... ready-to-paste HTML for About, Contact, Track Order,
                                 Size Guide, Shipping & Returns, FAQs.
   04_THEME_STYLING_GUIDE.txt .. exact Minimog Theme-Styling values (colours, type,
                                 buttons, borders) + UX recommendations.
   hero/hero_bg.png ............ your Itachi · Gojo · Maki hero background.

B) PRODUCTS  (folder: products/<slug>/)  — 890 products
   Each product folder contains:
     - info.txt ............. full human-readable product sheet (name, categories,
                              tags, price, stock, variations + SKUs, short & long
                              description in HTML, highlights, SEO title/meta,
                              image alt text, a Dark-Manga supplemental image prompt).
     - 01.jpg, 02.jpg ... ... the product photos (1,633 downloaded from your store).
     - _images.txt ......... filename -> original URL manifest.

C) WOOCOMMERCE IMPORT  (folder: build/)
   woocommerce_MASTER_import.csv .. THE ONE TO IMPORT. 890 products as 2,981 rows
                                    (407 variable + 483 simple + 2,091 variations).
   woocommerce_jerseys_import.csv . jerseys only (subset, if you want to test small).
   woocommerce_products.csv ....... everything except jerseys (subset).
   catalog.json / *.py ............ the build pipeline (re-runnable).

CATALOG SNAPSHOT
================
  890 products  |  407 variable (size/design/colour) + 483 simple  |  2,091 variations
  Prices in ₦ (Naira).  Images sideload automatically from the import URLs.
  Top categories: Accessories, T-Shirts (110), Hoodies (97), Katana & Weapons (42),
    Stickers (38), Jerseys (35), Figurines (35), Tote Bags (26), Chains, Headwear...
  Shop by Anime: Naruto 220, One Piece 149, Jujutsu Kaisen 95, Demon Slayer 76,
    Attack on Titan 74, Bleach 53, HxH, Berserk, Solo Leveling, Blue Lock, DBZ,
    Chainsaw Man, MHA, Tokyo Revengers.

HOW TO IMPORT TO WOOCOMMERCE
============================
 1. WordPress admin > Products > Import (or WooCommerce > scroll to Product CSV Importer).
 2. Upload  build/woocommerce_MASTER_import.csv.
 3. On the column-mapping screen, the headers match WooCommerce's native names, so
    they auto-map. Confirm "Attribute 1 name/value(s)/visible/global" map to attributes.
 4. Tick "Update existing products" only if re-importing. Run the importer.
 5. WooCommerce will SIDELOAD the images from the URLs (no manual media upload).
    Large catalog -> let it finish; consider importing in 2-3 passes if it times out
    (the jerseys / products subset CSVs are handy for that).
 6. After import: Products > Attributes — confirm "Size", "Style", "Color", "Material"
    exist. Set product image ALT text from each info.txt for SEO (optional but nice).
 7. SEO: the CSV fills Yoast title/meta (Meta: _yoast_wpseo_*). If you use Rank Math,
    map those columns to rank_math_title / rank_math_description instead.

DATA-QUALITY NOTES (quick clean-ups)
====================================
 • 13 rows import as "Uncategorized" — MOST are leftover Bumpa admin/test rows, NOT
   real products: "All Sales For 4th Week Jan 2026", "February Sales", "Vendor",
   "Item" (x2), "Others", "Death note". DELETE these before/after import.
   A few ARE real and just need a category: "Asta Jeans Jacket" + "Black Clover
   Jeans Jacket" (-> Apparel), "Thumb Sleeves" (-> Accessories), the "Customize(d/s)
   Case" entries (-> Phone Cases).
 • 1 product has a dead source image: products/kaneki-hoodie/ — its info.txt has a
   Dark-Manga Google Flow prompt to generate a replacement (Tokyo Ghoul hoodie).
 • "Featured" is left off for all products — pick your homepage hero products and
   tick "Featured" in WooCommerce so the Featured Products grid populates.
 • Prices/stock come straight from your Bumpa export. Spot-check a few before launch.

PIPELINE (re-runnable, in build/)
=================================
  build_catalog.py  -> download_images.py  -> gen_product_batches.py
  -> Workflow (AI content)  -> merge_batch.py  -> clean_content.py  -> render_products.py
  All content is AI-generated, self-reviewed, then post-processed to enforce ₦ currency,
  normalize franchises, and cap SEO title <=60 / meta <=155. No "official/licensed" claims.
################################################################################
