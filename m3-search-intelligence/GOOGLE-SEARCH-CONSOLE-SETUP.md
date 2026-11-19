# Google Search Console connection — preparation

M3 Search Intelligence currently accepts Search Console CSV exports. A direct connection requires OAuth authorization by the site owner.

## Google Cloud setup

1. Open Google Cloud Console and create or select a project you control.
2. Enable **Google Search Console API** for that project.
3. Configure the OAuth consent screen for an external/personal app as appropriate for your account.
4. Create an OAuth client with application type **Desktop app**.
5. Download the client JSON to the computer where M3SI will run.

## Keep credentials private

- Do not paste the client JSON, client secret, access token, or refresh token into chat.
- Do not commit credentials to GitHub or place them inside the website repository.
- Store the downloaded JSON outside the repository, with access limited to your user account.
- The future connector should request only the read-only scope:
  `https://www.googleapis.com/auth/webmasters.readonly`
- Token storage must remain local and be excluded from backups shared publicly.

## API access required

The connector will use the Search Console Search Analytics query endpoint for the verified property:
`https://samani12.github.io/m3alem-pro-site/`

It should request web search data by date and dimensions (query, page, device, country), respect Search Console row limits, and record the requested date range with every import. Search Console may omit anonymized or low-volume queries; API rows are not a complete census of all searches.

## Current status

This document is preparation only. No OAuth client, secret, or token has been created or stored by M3SI. CSV import remains available and is the active data path until the owner completes Google authorization.
