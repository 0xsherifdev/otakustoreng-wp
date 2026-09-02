export const meta = {
  name: 'otaku-homepage',
  description: 'Generate Dark-Manga homepage copy + Google Flow image prompts for Otaku Store NG (Minimog theme)',
  phases: [
    { title: 'Voice' },
    { title: 'Judge' },
    { title: 'Draft' },
    { title: 'Refine' },
  ],
}

const CTX = {"brand": "Otaku Store NG", "taglineRule": "Brand tagline must NOT reference Nigeria. It should be about anime fandom, gear, power, or wearing your favourite series. Short and ownable.", "style": "DARK MANGA aesthetic. Palette: ink black #111111, paper white #FAFAFA, and a single bold manga-red #E2261C accent (use sparingly for energy). Textures: halftone/screentone dots, manga speed lines, brush-ink splatter, manga panel layouts, high contrast monochrome with one red pop. Mood: premium anime-streetwear, bold, cinematic.", "market": "Based in Nigeria, ships nationwide AND internationally/worldwide. Prices in Nigerian Naira (₦). Trust signals: secure checkout, fast nationwide + worldwide delivery, easy returns. Do NOT make the brand identity Nigeria-only — it's a global anime brand that happens to ship from Nigeria.", "priceFacts": "Anime jerseys ₦23,000. Catalog ranges ₦1,000 (stickers/small accessories) to ₦250,000 (premium katana/figurines), median ~₦18,500. Free-shipping threshold and promos should feel realistic.", "categoryTree": {"Apparel": ["Jerseys", "T-Shirts", "Hoodies", "Kimono", "Trousers", "Shorts", "Headwear", "Shoes", "Ties", "Cosplay"], "Accessories": ["Chains & Necklaces", "Bracelets", "Rings", "Wallets", "Lanyards", "Phone Cases", "AirPods Cases", "Laptop Skins", "Masks", "Tote Bags", "Couple Accessories"], "Collectibles": ["Figurines", "Katana & Weapons", "Stickers", "Bottles & Drinkware"], "Home & Decor": ["Room Decor", "LED Lamps"], "Shop by Anime": ["Naruto", "One Piece", "Attack on Titan", "Demon Slayer", "Bleach", "Jujutsu Kaisen", "Dragon Ball", "Hunter x Hunter", "Berserk", "Solo Leveling", "Chainsaw Man", "My Hero Academia", "Tokyo Revengers"]}, "heroProducts": [{"type": "Anime Jerseys", "example": "Gojo / Itachi / Luffy all-over-print jerseys", "price": "₦23,000", "note": "signature product, vivid full-print"}, {"type": "Hoodies", "example": "Sukuna, Kaneki, Gojo hoodies", "note": "97 styles, streetwear staple"}, {"type": "Katana & Weapons", "example": "Tanjiro Nichirin blade, Zoro / Yubashiri katana", "note": "premium collectible display pieces"}, {"type": "Figurines", "example": "anime GK figures & statues", "note": "collector shelf pieces"}, {"type": "Chains & Necklaces", "example": "Akatsuki cloud, Uchiha, dog-tag chains", "note": "139 accessories, entry-price hype items"}, {"type": "Kimono", "example": "haori / kimono robes", "note": "statement layering pieces"}], "sectionMap": "You are mapping content onto the Minimog (Fashion demo) homepage. Fill EVERY numbered slot.\n\n1. ANNOUNCEMENT BAR (rotating, short) — 2-3 rotating messages (e.g. shipping, new drops, app).\n2. HEADER — logo wordmark idea, primary nav menu items (Home, Shop, New In, Anime, Blog, Track Order, Contact), search placeholder text, and the left \"SHOP BY CATEGORIES\" mega-menu (list the category tree).\n3. HERO SLIDER — 2 slides. Each: eyebrow, big headline, 1-line subtext, CTA button label, target. + IMAGE PROMPT for each slide.\n4. THREE PROMO BANNER CARDS (small grid under hero) — 3 cards, each: title, 1-line, CTA. + IMAGE PROMPT each.\n5. POPULAR CATEGORIES (icon row) — 7 category chips with label (pick best-sellers) + one IMAGE PROMPT describing the icon style for the whole row.\n6. TRENDING COLLECTION (3 large cards) — 3 cards: title + subtext. + IMAGE PROMPT each.\n7. WHAT'S TRENDING THIS WEEK (feature block) — a left feature panel (badge, headline, paragraph, CTA) + 2 product spotlight cards (name + price). + IMAGE PROMPT for the feature panel.\n8. FEATURED PRODUCTS (tabbed grid) — tab labels (by category/anime) + intro line. (Products auto-pull; just give the heading + tabs + a SALE-badge note.)\n9. PROMO / DEAL BAR — headline, deal line with ₦ price (strike + now), CTA. + IMAGE PROMPT background.\n10. SERVICE ICONS ROW — 4 trust badges, each: title + 1-line (shipping NG + worldwide, guarantee, support, secure payment).\n11. FOOTER — brand blurb (2 lines), 4 link columns (FIND IT FAST / CUSTOMER CARE / SHOP / COMPANY) with realistic links, newsletter heading + subtext + button label + consent microcopy, social handles line, payment methods line, copyright line.\n12. SEO / META — homepage <title> (<=60 chars) + meta description (<=155 chars).\n13. BRAND BONUS — final chosen tagline + 3 alternate taglines + a 2-3 sentence \"brand voice guide\" the user can reuse.", "outputRules": "- Output PLAIN TEXT (no markdown tables). Use clear section headers exactly like \"## SECTION 3 — HERO SLIDER\".\n- For every line of copy that replaces template text, prefix with \"REPLACE WITH:\" so it is obvious what to paste.\n- For every visual, add a line \"IMAGE PROMPT (Google Flow): <full prompt>\" including palette, texture, composition, aspect ratio (e.g. 16:9 hero, 1:1 cards, 3:4 promo), and \"no text overlay, no watermark\".\n- Keep it tight and skimmable. Real, paste-ready copy — not placeholders.\n- Use ₦ for all prices."};

const STYLE = `BRAND NAME: ${CTX.brand} (always written exactly like this).
TAGLINE RULE: ${CTX.taglineRule}
VISUAL STYLE (drives ALL image prompts): ${CTX.style}
MARKET: ${CTX.market}
PRICING FACTS (use real, do not invent absurd numbers): ${CTX.priceFacts}
HARD RULES:
- Currency is Nigerian Naira, symbol "₦". Show prices like ₦23,000.
- Never describe products as "official" or "licensed". They are fan / anime-inspired merch.
- Energetic, confident anime-fan voice. Speak to fans ("your roster", "your fit", "your shelf").
- No cringe. No excessive emojis (max 1 where it truly helps). No clichés like "unleash your inner".
- Image prompts must be COPY-PASTE ready for Google Flow / image generators: describe subject, composition, lighting, the Dark-Manga palette (ink black #111111, paper white #FAFAFA, single manga-red #E2261C accent), texture (halftone, speed lines, ink splatter, manga panels), aspect ratio, and "no text/no watermark" where the theme overlays text itself.`;

// ---------- schemas ----------
const VOICE_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['tagline', 'voice_summary', 'hero_headline', 'hero_subtext'],
  properties: {
    tagline: { type: 'string', description: 'Brand tagline, <= 6 words, NOT about Nigeria, about anime/fandom/gear' },
    voice_summary: { type: 'string', description: 'One sentence describing the tone of this angle' },
    hero_headline: { type: 'string', description: 'Hero slide headline, punchy' },
    hero_subtext: { type: 'string', description: 'Hero supporting line, 1 sentence' },
  },
};
const JUDGE_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['chosen_tagline', 'alt_taglines', 'voice_guide', 'rationale'],
  properties: {
    chosen_tagline: { type: 'string' },
    alt_taglines: { type: 'array', items: { type: 'string' }, minItems: 2, maxItems: 4 },
    voice_guide: { type: 'string', description: 'Merged voice guidance, 2-3 sentences, for the copywriter to follow' },
    rationale: { type: 'string' },
  },
};

// ---------- Phase 1: explore distinct voice/tagline angles ----------
phase('Voice');
const ANGLES = [
  { key: 'battle', lean: 'Battle/power energy — gearing up like preparing for a fight, bold and hype, manga-action vibe.' },
  { key: 'collector', lean: 'Collector/curation energy — premium, "build your collection", for the devoted fan who wants the real grail pieces.' },
  { key: 'streetwear', lean: 'Anime-streetwear energy — fashion-forward, "wear your fandom on the street", drip-and-culture vibe.' },
];
const voices = (await parallel(ANGLES.map(a => () =>
  agent(`You are a world-class DTC brand copywriter for an ANIME MERCH store. Propose a brand voice for this angle.\n\nANGLE: ${a.key} — ${a.lean}\n\n${STYLE}\n\nReturn a tagline (NOT about Nigeria), a one-line voice summary, a hero headline and hero subtext that fit this angle.`,
    { label: `voice:${a.key}`, phase: 'Voice', schema: VOICE_SCHEMA })
))).filter(Boolean);

// ---------- Phase 2: judge + merge ----------
phase('Judge');
const judged = await agent(`You are a senior brand strategist for anime/streetwear DTC brands. Below are ${voices.length} candidate brand-voice directions for "${CTX.brand}".\n\nCANDIDATES:\n${JSON.stringify(voices, null, 2)}\n\n${STYLE}\n\nPick the single strongest tagline (memorable, ownable, NOT Nigeria-themed, captures anime fandom). Provide 2-4 strong alternates. Write a merged voice guide (2-3 sentences) blending the best instincts of the candidates for the copywriter to follow.`,
  { label: 'judge', phase: 'Judge', schema: JUDGE_SCHEMA });

// ---------- Phase 3: full homepage draft ----------
phase('Draft');
const draft = await agent(`You are the lead copywriter building the homepage for "${CTX.brand}", an anime merch store on the Minimog WooCommerce theme. Produce the COMPLETE section-by-section content replacement document.\n\nUSE THIS VOICE:\nTagline: ${judged.chosen_tagline}\nVoice guide: ${judged.voice_guide}\n\n${STYLE}\n\nCATEGORY TREE (for the mega-menu + category sections, use these real categories):\n${JSON.stringify(CTX.categoryTree, null, 2)}\n\nHERO / FEATURE PRODUCT IDEAS (real products in the store):\n${JSON.stringify(CTX.heroProducts, null, 2)}\n\nYou MUST fill EVERY numbered section of this Minimog section map:\n${CTX.sectionMap}\n\nOUTPUT FORMAT RULES:\n${CTX.outputRules}\n\nWrite the full document now as plain text following the format rules. Be specific, on-brand, and conversion-focused. Every visual slot must include a "IMAGE PROMPT (Google Flow):" line.`,
  { label: 'draft', phase: 'Draft' });

// ---------- Phase 4: refine + completeness critic ----------
phase('Refine');
const final = await agent(`You are a senior DTC copy chief AND conversion-rate specialist reviewing a homepage content document for "${CTX.brand}".\n\nYOUR JOB: return an IMPROVED, FINAL version of the FULL document. Specifically:\n1. Verify EVERY numbered section from the section map below is present and filled. If any is missing, add it.\n2. Tighten copy: punchy, on-voice (${judged.chosen_tagline}), no clichés, no fluff, no "official/licensed" claims.\n3. Ensure every visual slot has a copy-paste-ready Google Flow IMAGE PROMPT in the Dark-Manga style (ink black #111111 / paper white #FAFAFA / manga red #E2261C, halftone, speed lines, ink splatter, manga panels), with aspect ratio and "no text overlay".\n4. Ensure prices use ₦, market framing welcomes Nigeria + international, and the tagline is NOT Nigeria-specific.\n5. Keep section labels/numbering so it's easy to map to Minimog.\n\nSECTION MAP (the required sections):\n${CTX.sectionMap}\n\n${STYLE}\n\nDOCUMENT TO IMPROVE:\n${draft}\n\nReturn ONLY the full improved document text.`,
  { label: 'refine', phase: 'Refine' });

return { tagline: judged.chosen_tagline, alt_taglines: judged.alt_taglines, voice_guide: judged.voice_guide, doc: final };
