export const meta = {
  name: 'otaku-jerseys-pilot',
  description: 'Write WooCommerce-ready product content for the Jerseys pilot category (write -> adversarial verify/repair)',
  phases: [
    { title: 'Write' },
    { title: 'Verify' },
  ],
}

const JERSEYS = /*JERSEYS_JSON*/;
const STYLE = /*STYLE_JSON*/;

const PRODUCT_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['franchise', 'character', 'subtitle', 'short_description', 'long_description_html',
             'highlights', 'seo_title', 'meta_description', 'focus_keyword', 'tags',
             'image_alt', 'supplemental_image_prompt'],
  properties: {
    franchise: { type: 'string', description: 'Anime series this is from, inferred from the title/character if not given. Use "Generic Anime" if truly unknown.' },
    character: { type: 'string', description: 'Main character featured (from the title), or "" if none.' },
    subtitle: { type: 'string', description: 'Short punchy product subtitle / hook, <= 12 words.' },
    short_description: { type: 'string', description: 'WooCommerce excerpt, 25-45 words, benefit-led.' },
    long_description_html: { type: 'string', description: 'Full WooCommerce description in clean HTML: 1-2 <p> paragraphs then a <ul><li> spec list (material, print, fit, sizing, care). No <h1>.' },
    highlights: { type: 'array', items: { type: 'string' }, minItems: 4, maxItems: 6, description: 'Bullet selling points.' },
    seo_title: { type: 'string', description: 'SEO title, MUST be <= 60 characters, include character/franchise + "Anime Jersey".' },
    meta_description: { type: 'string', description: 'Meta description, MUST be <= 155 characters, compelling + keyword.' },
    focus_keyword: { type: 'string', description: 'Primary SEO keyword phrase.' },
    tags: { type: 'array', items: { type: 'string' }, minItems: 4, maxItems: 10, description: 'WooCommerce tags: character, franchise, "anime jersey", style keywords.' },
    image_alt: { type: 'string', description: 'Descriptive alt text for the primary product photo.' },
    supplemental_image_prompt: { type: 'string', description: 'Google Flow Dark-Manga style prompt for an optional lifestyle/studio shot to supplement the catalog photo.' },
  },
};

const VERDICT_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['pass', 'issues', 'fixed'],
  properties: {
    pass: { type: 'boolean', description: 'true if the original content was already fully correct and compliant.' },
    issues: { type: 'array', items: { type: 'string' }, description: 'Problems found (franchise wrong, SEO title >60, meta >155, "official/licensed" claims, hallucinated specifics, sizing wrong, etc.).' },
    fixed: PRODUCT_SCHEMA,
  },
};

function sizesOf(j) {
  const s = j.variants.map(v => v.name);
  return s.length ? s.join(', ') : '(no size variants entered — treat as one-size / advise sizes M-3XL)';
}

function writePrompt(j) {
  return `You are an expert anime-merch copywriter writing a WooCommerce product listing for "${STYLE.brand}".\n\n${STYLE.text}\n\nPRODUCT KNOWLEDGE — ANIME JERSEY:\n${STYLE.jerseyKnowledge}\n\nTHIS PRODUCT:\n- Title: ${j.title}\n- Detected franchise (may be blank, infer from name): ${j.franchises.join(', ') || '(infer)'}\n- Price: ₦${(j.price_min || 23000).toLocaleString('en-US')}\n- Available sizes: ${sizesOf(j)}\n- Existing description (often a placeholder like "Quality Jersey"): ${j.description_text || '(none)'}\n- Number of catalog photos: ${j.images.length}\n\nWrite compelling, accurate, SEO-optimised content. Identify the franchise/character from the title (e.g. "Akaza" -> Demon Slayer, "Chopper" -> One Piece, "Gojo/Gojou" -> Jujutsu Kaisen, "Goku" -> Dragon Ball, "Ichigo" -> Bleach, "Itachi" -> Naruto). If a name is ambiguous or a person's name with no clear anime link, set franchise to "Generic Anime" and character to "". Keep SEO title <= 60 chars and meta description <= 155 chars. Do NOT claim official/licensed.`;
}

function verifyPrompt(j, content) {
  return `You are a strict QA editor for anime-merch e-commerce listings. Review the content below for the product "${j.title}" (sizes: ${sizesOf(j)}, price ₦${(j.price_min || 23000).toLocaleString('en-US')}).\n\n${STYLE.text}\n\nCHECK FOR:\n- Wrong franchise/character (verify against the title — fix if wrong).\n- SEO title > 60 characters (must fix to <= 60).\n- Meta description > 155 characters (must fix to <= 155).\n- Any "official", "licensed", "authentic licensed" or trademark-claiming language (remove).\n- Hallucinated specifics not supported (invented fabric weights, fake awards, fake reviews) — keep claims generic-true for sublimated polyester anime jerseys.\n- Sizing claims that contradict the available sizes.\n- HTML validity in long_description_html (clean <p>/<ul>/<li>, no <h1>).\n\nReturn pass=true only if NOTHING needs changing. ALWAYS return the corrected full content in "fixed" (if already perfect, return it unchanged).\n\nCONTENT TO REVIEW:\n${JSON.stringify(content, null, 2)}`;
}

log(`Writing + verifying ${JERSEYS.length} jersey listings`);
const results = await pipeline(
  JERSEYS,
  j => agent(writePrompt(j), { label: `write:${j.slug}`, phase: 'Write', schema: PRODUCT_SCHEMA }),
  (content, j) => agent(verifyPrompt(j, content), { label: `verify:${j.slug}`, phase: 'Verify', schema: VERDICT_SCHEMA })
       .then(v => ({ slug: j.slug, product_id: j.product_id, content: v.fixed || content, passed_clean: v.pass, issues: v.issues || [] }))
);

return results.filter(Boolean);
