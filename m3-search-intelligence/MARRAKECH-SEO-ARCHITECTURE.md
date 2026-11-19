# M3 Marrakech SEO Intelligence — V1

## Purpose
A deterministic, explainable local SEO prioritization engine for M3ALEM-PRO in Marrakech. It combines the existing crawler and Search Console CSV data with service classification, local-intent detection, commercial-intent detection, page mapping and content briefs.

## Integrated architecture

1. **Collection layer** — existing same-host crawler and manual CSV import from Search Console/Bing. Future authorized connectors can feed the same normalized row format.
2. **Normalization layer** — Unicode/diacritic normalization; Arabic, French and Latin keyword matching.
3. **Intent classifier** — identifies service, Marrakech/local signals, transactional intent and informational intent.
4. **Opportunity engine** — transparent weighted score using impressions, local relevance, service match, commercial intent, CTR headroom, average-position range and click signal.
5. **Page mapper** — maps each recognized service query to the existing service landing page to reduce keyword cannibalization.
6. **Content planner** — creates structured briefs, not auto-published pages.
7. **Dashboard** — displays the local priority and recommended page beside existing GSC metrics.

## Score interpretation
The 0–100 score is a prioritization heuristic, not a Google ranking forecast, search-volume estimate, or lead guarantee. Each component is returned in `factors` so the score can be audited. Thresholds: high >=65, medium >=35, otherwise low.

## Run
From `m3-search-intelligence`:
```bash
python app.py
```
Open `http://127.0.0.1:8765`. Import a Search Console Queries CSV to activate local opportunity rows.

## Safety and quality controls
- No scraping of Google/Bing result pages.
- No automated backlinks, fake reviews, fabricated business details or doorway pages.
- No automatic publication or modification of the public website.
- Existing service URLs are preferred; new pages require a unique service need and human review.
- Content briefs prohibit invented prices, addresses, testimonials, guarantees and availability.
- The engine works on available imported data; no current ranking or competitor position is assumed without a source.

## Next integrations
- Google Search Console API after owner OAuth authorization.
- Google Business Profile metrics after supported account authorization.
- Meta Insights after Page/Instagram business account authorization.
- Lead attribution by tagged WhatsApp/call links and a manually maintained lead outcome log.
