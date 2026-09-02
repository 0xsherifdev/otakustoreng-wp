export const meta = {
  name: 'otaku-products',
  description: 'Write WooCommerce-ready, category-aware product content (single self-reviewing agent per product)',
  phases: [{ title: 'Write' }],
}

const PRODUCTS = /*PRODUCTS_JSON*/;
const STYLE = /*STYLE_JSON*/;

const PRODUCT_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['franchise', 'character', 'subtitle', 'short_description', 'long_description_html',
             'highlights', 'seo_title', 'meta_description', 'focus_keyword', 'tags',
             'image_alt', 'supplemental_image_prompt'],
  properties: {
    franchise: { type: 'string', description: 'Anime series, inferred from the title/character if not given. "Generic Anime" if truly unknown.' },
    character: { type: 'string', description: 'Main character featured (from the title), or "".' },
    subtitle: { type: 'string', description: 'Short punchy product subtitle / hook, <= 12 words.' },
    short_description: { type: 'string', description: 'WooCommerce excerpt, 25-45 words, benefit-led, accurate to the product type.' },
    long_description_html: { type: 'string', description: 'Full WooCommerce description: 1-2 <p> then a <ul><li> spec list appropriate to THIS product type (materials, dimensions, what is included, compatibility, care). Clean HTML, no <h1>. Do NOT restate the price or shipping as bullets.' },
    highlights: { type: 'array', items: { type: 'string' }, minItems: 4, maxItems: 6 },
    seo_title: { type: 'string', description: 'SEO title, MUST be <= 60 characters.' },
    meta_description: { type: 'string', description: 'Meta description, MUST be <= 155 characters.' },
    focus_keyword: { type: 'string' },
    tags: { type: 'array', items: { type: 'string' }, minItems: 4, maxItems: 10 },
    image_alt: { type: 'string', description: 'Descriptive alt text for the primary product photo.' },
    supplemental_image_prompt: { type: 'string', description: 'Google Flow Dark-Manga style prompt for an optional supplemental studio/lifestyle shot.' },
  },
};

function naira(n) { return '₦' + (Number(n) || 0).toLocaleString('en-US'); }
function optionLine(p) {
  if (p.attr_name && p.option_values && p.option_values.length)
    return `${p.attr_name} options: ${p.option_values.join(', ')}`;
  return '(single option / no variants)';
}

function buildPrompt(p) {
  return `You are an expert anime-merch copywriter creating a WooCommerce product listing for "${STYLE.brand}".\n\n${STYLE.text}\n\nPRODUCT CATEGORY: ${p.category}\nCATEGORY KNOWLEDGE (use for accurate specs; do NOT invent exact measurements, weights, or certifications):\n${p.knowledge}\n\nTHIS PRODUCT:\n- Title: ${p.title}\n- Category: ${p.category}${p.all_categories.length > 1 ? ' (also tagged: ' + p.all_categories.join(', ') + ')' : ''}\n- Detected franchise (may be blank — infer from the title): ${p.franchises.join(', ') || '(infer)'}\n- Price: ${naira(p.price_min)}\n- ${optionLine(p)}\n- Existing description (often a weak placeholder): ${p.description_text || '(none)'}\n- Catalog photos: ${p.n_images}\n\nWrite compelling, accurate, SEO-optimised content tailored to a ${p.category} product. Identify the franchise/character from the title where possible (e.g. Itachi/Akatsuki/Sasuke -> Naruto; Luffy/Zoro/Chopper -> One Piece; Gojo/Sukuna -> Jujutsu Kaisen; Tanjiro/Nezuko/Akaza -> Demon Slayer; Ichigo -> Bleach; Goku/Vegeta -> Dragon Ball; Isagi -> Blue Lock; Guts -> Berserk; Eren/Levi -> Attack on Titan). If a name has no clear anime link, set franchise to "Generic Anime" and character to "".\n\nTHEN SELF-REVIEW your draft and FIX any issue before outputting:\n  • franchise/character correct for the title;\n  • seo_title <= 60 characters; meta_description <= 155 characters;\n  • NO "official"/"licensed"/trademark-claiming language (fan / anime-inspired, not affiliated);\n  • no invented measurements/weights/certifications — keep claims true-to-type for a ${p.category};\n  • long_description_html = 1-2 <p> then a <ul> spec list relevant to a ${p.category}, clean HTML, no <h1>, do not restate price/shipping as bullets;\n  • on-voice; use ₦ for any price.\n\nReturn the corrected final content via the StructuredOutput tool.`;
}

log(`Writing ${PRODUCTS.length} product listings (single-agent self-review)`);
const results = await pipeline(
  PRODUCTS,
  p => agent(buildPrompt(p), { label: `write:${p.slug}`, phase: 'Write', schema: PRODUCT_SCHEMA })
        .then(c => ({ slug: p.slug, product_id: p.product_id, content: c, passed_clean: true, issues: [] }))
);

return results.filter(Boolean);
