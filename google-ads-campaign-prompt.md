# Reusable prompt: build a Google Ads campaign for any website in Claude Code

Paste this into any Claude Code project that (a) has a live website you want to advertise,
and (b) has the Supermetrics MCP connected with Google Ads write access enabled
(hub.supermetrics.com/write-settings?platform=AW). Fill in the bracketed parts.

---

I want you to build a Google Ads Search campaign for [WEBSITE URL], focused only on
[TOPIC / PRODUCT LINE — e.g. "corporate gifting", not general retail sales]. Do this
properly, don't guess — here's the process:

1. **Scan the live site first.** Browse it, read the nav/menu, check what product
   categories, collections, and price bands actually exist, and find (or note the
   absence of) any dedicated landing page for [TOPIC]. Use real page URLs as ad
   landing pages — don't invent pages that don't exist.

2. **Check the connected Google Ads account** (accounts_discovery, ds_id "AW") and
   look at existing campaigns (campaign_and_resource_get, resource_type "campaigns")
   before creating anything new, so we don't duplicate or conflict with what's already
   there.

3. **Do real keyword research** via campaign_and_resource_get with resource_type
   "keyword_ideas" — pass 5-6 seed keywords per call (more gets silently truncated),
   plus the site URL. Pull search volume, competition, and CPC ranges. Don't invent
   keyword lists from general knowledge — use what the tool actually returns, and tell
   me honestly which themes have real search volume and which are thin long-tail.

4. **Structure it as multiple tightly-themed ad groups** (not one big bucket) — e.g.
   split by buyer intent, budget band, occasion/season, or industry vertical, whatever
   the keyword research actually supports. Each ad group gets its own landing page
   (the most relevant real page from step 1) and its own Responsive Search Ad:
   5-7 headlines (max 30 chars), 2-3 descriptions (max 90 chars), written from the
   site's actual content — real stats, real phone number, real claims. No fabricated
   numbers.

5. **Add campaign-level negative keywords** to filter obviously irrelevant traffic
   (jobs, free, resume, internship, recruitment, second hand, etc. — adjust for the
   topic).

6. **Always create the campaign PAUSED first.** Tell me the daily budget you're about
   to set — if I haven't already told you a number, ask me before creating anything,
   since campaign creation requires a budget_amount. Show me the full built structure
   (ad groups, keyword counts, ad copy, landing pages) before asking whether to enable
   it — enabling starts real spend, so always get my explicit go-ahead for that specific
   step, separately from building it.

7. **Be honest about budget-vs-CPC reality.** If keyword CPCs are high relative to the
   daily budget, tell me plainly how many clicks/day that budget realistically buys —
   don't let me assume more volume than the numbers support.

8. If the `google-ads-write`, `google-ads-audit`, or `google-ads-math` skills are
   available in this project, use them for the write protocol and any budget/CPC math.
   If they're not installed, offer to install them from
   https://github.com/itallstartedwithaidea/agent-skills (the current maintained repo;
   itallstartedwithaidea/google-ads-skills is the older, superseded version).

---
