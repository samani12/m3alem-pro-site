# M3 Search Intelligence — Marrakech SEO V1

A locally owned SEO intelligence workspace for the M3ALEM-PRO website.

## What this version does
- Ignores non-web links such as mailto:, tel: and javascript: instead of aborting a crawl.
- Caps crawler page count, timeout and delay values to conservative limits.
- Crawls only the configured website host, with a page limit, timeout, robots.txt checks and same-host redirect protection.
- Stores page metadata in a local SQLite database.
- Imports Google Search Console / Bing Webmaster CSV exports, including common French and Arabic column labels and decimal-comma values.
- Scores query opportunities using impressions, CTR gap, and average position.
- Classifies Arabic/French/Latin local queries for Marrakech and service intent.
- Ranks local commercial opportunities and maps them to existing service pages.
- Generates safe content briefs for the six existing service categories.
- Integrates local SEO priorities into the Arabic dashboard.
- Shows a local Arabic dashboard.

See [MARRAKECH-SEO-ARCHITECTURE.md](MARRAKECH-SEO-ARCHITECTURE.md) for scoring factors, architecture and safety rules.

## What it does NOT do yet
- It is not hosted or continuously running.
- It is not yet connected to Google or Bing APIs; CSV export is the first data path.
- It does not scrape search-engine result pages, create backlinks, or publish website edits automatically.
- GitHub Pages cannot run this Python backend. Run locally or deploy later to a Python-capable host.

## Run (Windows / macOS / Linux)
Python 3.10+ recommended. No third-party packages required.

```bash
cd m3-search-intelligence
python app.py
```
Open http://127.0.0.1:8765

Optional:
```bash
M3SI_SITE_URL=https://samani12.github.io/m3alem-pro-site/ python app.py
```

## Import search data
Export a CSV from Search Console (Performance → Search results → Queries or Pages) or Bing Webmaster Tools. Upload it in the dashboard. The importer recognizes common column names such as Query, Clicks, Impressions, CTR, Position / Average position.

## Data ownership
Database: `data/m3si.sqlite3` on the machine running the app. Back it up regularly. No API keys are stored in this repository.

## Safety
The crawler is read-only. It respects robots.txt, limits pages, uses a delay, blocks cross-host redirects, and does not execute JavaScript. Search opportunities are recommendations, not promises of rankings or leads.

## Roadmap
1. OAuth-based Search Console API connection.
2. Bing Webmaster API connection.
3. Local Business Profile metrics import.
4. Change proposals with before/after diff, approval, backup and rollback.
5. Scheduled runs only after a reliable host and explicit credentials are configured.
