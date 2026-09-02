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

const CTX = /*CTX_JSON*/;

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
