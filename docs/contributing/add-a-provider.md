# Add a provider

Use this workflow for both source investigation and implementation. A provider is not registered until public official-source proof and the runtime, site, inventory, tests, workflow, and documentation changes agree.

## 1. Prove the source boundary

- Choose a stable snake-case `provider_id`.
- Identify official entry points, stable event and attachment identities, availability semantics, access restrictions, payload types, and update cadence.
- Reject authentication-gated, non-enumerable, third-party-only, or non-paper sources unless the product scope explicitly changes.
- Record an investigated but unshipped source under `candidates` in `catalog/source-inventory.json`; do not create a provider page or adapter for it.

## 2. Define ownership and contracts

- Provider state: `data/providers/<provider_id>/` and `mirror/providers/<provider_id>/`.
- Site publication: `data/sites/<site_id>/` and `bundles/sites/<site_id>/`.
- Map source records into the normalized schema and deterministic identity catalog.
- Define discovery, manifest behavior, payload validation, failure semantics, aliases, and source-coverage exceptions.
- Decide which site consumes the provider and whether its bundle or shard policy changes.

## 3. Implement and register

- Add the provider adapter under `app/providers/<provider_id>/`.
- Register it in `app/providers/registry.py` and the consuming site in `app/site_registry.py`.
- Add the provider entry to `catalog/source-inventory.json` with reviewed evidence.
- Add source-specific parser, discovery, validation, state, publication, and workflow tests as applicable.
- Add or update provider sync automation and operator recovery steps.

## 4. Write source judgment

Run the renderer to create `docs/providers/<provider_id>.md`, then maintain its five judgment sections:

- Source boundary: what official material is eligible and how ambiguity is resolved.
- Gaps and blockers: durable explanation, without copying inventory status or counts.
- Publication shape: exceptional bundle, quarantine, or site behavior.
- Operating it: only provider-specific deviations from the shared runbook.
- Open decisions: links to ADRs or issues, never an embedded execution plan.

Do not edit frontmatter or generated inventory blocks. Changing facts such as status, URLs, years, record counts, or restrictions starts in `catalog/source-inventory.json`.

## 5. Verify definition of done

```bash
uv run python scripts/render_docs.py
uv run python scripts/validate_source_inventory.py
uv run python scripts/validate_docs.py --check
uv run python -m pytest -q
uv run python -m app audit-catalog --repo-root . --site-id default --strict
uv run python -m app history-audit --repo-root . --site-id default --strict --skip-mirror-check
```

The change is incomplete if any registered provider lacks a page, any page lacks a provider, generated state is unscoped, publication ownership is unclear, or an operator cannot recover the provider without reading implementation code.
