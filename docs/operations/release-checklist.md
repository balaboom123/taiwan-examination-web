# Release checklist

## Preflight

```bash
uv run python -m pytest -q
uv run python scripts/validate_source_inventory.py
uv run python scripts/validate_publication.py
uv run python scripts/render_docs.py
uv run python scripts/validate_docs.py --check
uv run python -m app audit-catalog --repo-root . --site-id default --strict --output .tmp/catalog-audit.json
uv run python -m app history-audit --repo-root . --site-id default --strict --output .tmp/history-audit.json
uv run python -m app plan-release --repo-root . --site-id default --output .tmp/release-plan.json
```

With the persistent mirror available, do not use `--skip-mirror-check`.

## Build the site projection

```bash
uv run python -m app publish-site --site-id default --repository <owner>/<repo>
uv run python -m app plan-release --repo-root . --site-id default --output .tmp/release-plan.json
```

Review provider failures, publication quarantine, expected asset names, release tags, and the release plan before uploading anything.

## Frontend verification

```bash
cd frontend
npm test
npm run lint
npm run build
```

## Publish and verify

Use the repository release workflow to ensure and upload expected site assets. Prune only after expected assets are present and the generated inventory proves which external assets are stale. Deploy the site, verify representative bundle URLs across release shards, and retain the audit reports for the release review.
