# Ready-to-use prompt: generate a client gifting PPT

Paste the block below as your **first message** in a new Claude Code session
opened in this project folder (`master price list`). Fill in the three
`{{ }}` placeholders — nothing else needs editing, and no follow-up
instructions should be necessary.

This works because the session has direct access to this project's live
product data (`_catalog_build/output/master_consolidated.json` — the same
data that powers corporategiftingindia.co) and to the `budget-gift-ppt`
skill already built here, which knows the full deck structure, house style,
and sourcing rules. You are not asking Claude to invent a deck design from
scratch each time — you're asking it to run the established pipeline with
your three inputs.

---

## The prompt

```
Use the budget-gift-ppt skill to build a corporate gifting proposal deck
with these three inputs:

- Client category (industry/vertical): {{CLIENT_CATEGORY}}
- Budget (max tax-paid price per gift, INR): {{BUDGET}}
- Client name: {{CLIENT_NAME}}

Pull all products, pricing and images from this project's own master
catalogue (_catalog_build/output/master_consolidated.json — the same data
behind corporategiftingindia.co) — don't ask me for a product list.

Build the full proposal structure the skill defines: cover (client
branding + category + budget), table of contents, category overview,
product showcase (photo/brand/name/MRP/2 features per product, ~25-30
options), a comparison table of top picks, a "Why Nalanda Enterprises"
credibility slide (real stats only — years trading, brand count, catalog
size, verified-MRP sourcing practice; no invented testimonials or
quotes), terms & conditions, and a closing/contact slide.

If I've attached a client logo or reference photos earlier in this
conversation, use them for cover/closing branding. If not, proceed
without them — don't block on asking, just build the deck using the
navy/teal house style on its own.

Use the highest-resolution real product images actually available in the
catalogue or sourced fresh from the official brand site / Amazon /
Flipkart for any named must-include item not already in the catalogue —
never fabricate a resolution claim (e.g. don't label an image "8K" unless
it genuinely is).

QA the deck (structural validation, content check, visual spot-check),
compress images so the file stays under ~10MB, then deliver it as a
.pptx file.
```

---

## Notes for future you

- **Where the three variables go**: they're the three bullet lines near the
  top of the prompt. Nothing else needs to change per client.
- **If you want a logo/photos used**: attach them in the same message (or
  right before sending the prompt) — Claude will find them in the
  conversation automatically.
- **If you want fewer/more products** than the default ~25-30, add a line
  like `Total products: 20` to the prompt.
- **If you want to force specific products in**, add a line like
  `Must include: boAt Bassheads 100, Swiss Military Pulse Pro` — the skill
  resolves these to catalogue entries and includes them regardless of the
  budget-pool selection logic.
- **The skill lives at** `.claude/skills/budget-gift-ppt/` in this project
  (`SKILL.md` + `scripts/select_products.py` + `scripts/build_gift_ppt.js`).
  If you ever want to change the deck's design, slide structure, or default
  terms & conditions wording, edit `SKILL.md` there — this prompt file
  doesn't duplicate that logic, it just triggers it.
