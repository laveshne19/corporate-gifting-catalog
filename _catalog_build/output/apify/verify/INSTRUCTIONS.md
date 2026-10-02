# Product photo verification — instructions for each chunk agent

The site owner found wrong photos on the live catalog (e.g. a Honda Activa scooter showing a
smartwatch). Owner's rule: **a product keeps a photo only if it is confirmed to be the exact same
product as its name. If no exact match can be confirmed, the photo is removed ("Image on request").**
Your job: for every product in your chunk, confirm the current photo, or find the exact correct
photo, or report that none can be confirmed.

Edit NOTHING except your own output file.

## Input / output
- Input: `vchunk_<N>.json` in this folder — list of
  `{product_id, brand, product_name, model_code, category, sub_category, current, query}`.
  `current` is the photo URL shown on the site today.
- Output: `/home/user/corporate-gifting-catalog/_catalog_build/output/apify/verify_results_<N>.json`
  — JSON list, one entry per input product, input order:
  `{"product_id", "keep": true|false, "image_url": <url or null>, "confidence": "high"|null,
    "source_domain", "matched_title"}`
  - Current photo confirmed → `"keep": true, "image_url": null`.
  - Current photo not confirmed but an exact-match photo found → `"keep": false, "image_url": <new>, "confidence": "high"`.
  - Neither → `"keep": false, "image_url": null, "confidence": null` (photo will be removed).
  Write the file after every batch so work is not lost. Scratch files go ONLY in your own
  folder `/tmp/claude-0/-home-user-corporate-gifting-catalog/747d7900-7bfa-5bac-bcee-91739039205e/scratchpad/v<N>/`
  (the scratchpad is shared with other agents).

## Tools
ToolSearch `select:mcp__apify_john_google_image__johnvc--google-images-api,mcp__Apify_google_image__get-dataset-items,mcp__Apify_google_image__get-actor-run`.
Direct HTTP to apify / image hosts is blocked — use only these MCP tools. Apify allows max 32
concurrent runs account-wide; if a run is rejected for concurrency, wait briefly (poll another
run) and retry. Transient 502s: retry.

## Steps
1. Batches of ~32 products: call `johnvc--google-images-api` with `queries` = the products'
   `query` values in order, `gl="in"`, `hl="en"`, `maxResultsPerQuery=50`, `waitSecs=45`; poll
   `get-actor-run` (waitSecs 45) until SUCCEEDED.
2. Query i's results start at about offset 50*i. For each product call `get-dataset-items`
   with `offset=50*i, limit=8, fields="query,position,title,imageUrl,imageWidth,domain"`.
   ALWAYS check the returned `query` equals the product's query. If not (a query returned
   fewer than 50 images, or identical queries were merged), find the right block by probing
   with `fields="query,position"` and small limits. Never fetch large pages.
3. Decide per product:
   - **Title match** means: the result title (or the image file name when it spells the exact
     model code) names the same brand AND the exact model / name / capacity / size, AND the
     product type is the same (earbuds ≠ smartwatch ≠ speaker; AC ≠ fridge; scooter ≠ watch).
     Colour variants: must match when the product name states a colour.
     A title naming a different generation or sub-model is NOT a match (e.g. "SlideMate 2" for
     "SlideMate", "BlueFi Nano" for "Bluefi", "Pro"/"Lite"/"Max" suffixes that the product lacks).
     Only write rows after you have actually decided them — never pre-fill placeholder rows.
   - **keep = true** if the `current` URL is the same image as a result whose title matches —
     compare by URL, or by the same image ID/file name on the same host (e.g. Amazon
     `/images/I/<ID>` ignoring size suffixes, Flipkart path ignoring the `/image/<w>/<h>/` size,
     Shopify file name ignoring `?v=` / `&width=`).
   - Otherwise pick the best **title-matched** result as the new `image_url` (confidence "high").
     Prefer brand official sites, `m.media-amazon.com` full-size (strip `._AC_...` suffix),
     `rukmini*.flixcart.com`, croma, reliancedigital/jiostore, tatacliq; width ≥ 500.
   - Never use: corporategiftingindia.co, lab4brands, alienfox, pinterest/pinimg, instagram,
     facebook/fbsbx, x.com/twimg, gstatic `encrypted-tbn` thumbnails, YouTube thumbnails,
     second-hand marketplaces.
   - If nothing is a confirmed exact match → keep false, image_url null. Do NOT return a
     "close enough" sibling model, different capacity, or different colour.
4. At the end validate with python: JSON loads, same length and product_id order as input.

Reply with a short summary only: counts keep / replaced / removed, and any rows that are clearly
not real products (junk data rows).
