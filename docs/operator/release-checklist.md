# Public release checklist

GitHub Pages is the canonical production host for the `default` site. Netlify is retained for deploy previews only; preview builds must not load production advertising or be treated as the canonical URL.

## Pre-merge gates

Run the same checks required by `.github/workflows/ci.yml`:

```bash
uv run pytest -q
python -m app audit-catalog --repo-root . --site-id default --output .tmp/catalog-audit.json
python scripts/validate_publication.py
python -m app plan-release --repo-root . --site-id default --output .tmp/release-plan.json
cd frontend
npm ci
npm test
npm run lint
npm run build
```

The public catalog gate must report:

- every published bundle has `high` or `medium` classification confidence;
- every generic skill/admission bundle has a subject label and searchable aliases;
- the frontend feed, site inventory, and release inventory describe the same logical and physical assets;
- every release shard stays at or below the 900-asset safety target;
- workflow contract tests and shell syntax checks pass.

## Publish and smoke test

1. Merge the release candidate into `main` only after the Python and frontend CI jobs pass.
2. Confirm the Pages deployment completes and the site URL is the repository Pages URL.
3. On a phone-sized viewport, search for `護理師`, `律師`, `冷凍空調裝修`, `數學A`, and one TCTE group.
4. Use the category, subclass, ROC-year, sort, and share-link controls; reload a copied URL and confirm the same result appears.
5. Open at least five different download assets from different release shards. Confirm the response is a ZIP, it opens, and the archive contains PDFs.
6. Check `robots.txt`, `sitemap.xml`, canonical URLs, the FAQ/privacy/contact pages, and keyboard focus behavior.
7. Record the deployment run, release tags, smoke-test URLs, and any missing source papers in the release issue.

## Recovery

If a provider sync fails, keep the prior site inventory and use the provider-specific recovery procedure. Do not delete a release shard or prune assets until the regenerated `release-assets.json` passes the publication validator. If Pages fails, restore the last known-good `main` deployment and investigate the CI/build artifact before changing release data.

## Remaining risks

- Download access is a client-side local-storage gate; it is a growth mechanism, not membership verification or access control.
- Source availability, copyright ownership, and takedown requests remain provider-specific and require operator review before paid promotion.
- Provider state can contain review-confidence records that are intentionally isolated from the public catalog; a non-zero review queue is not safe to ignore when changing provider mappings.
- Frontend checks must remain green on GitHub Actions because the local development environment may not have the required Node/npm toolchain.
