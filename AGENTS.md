# Repository instructions

This repository is maintained primarily by AI agents and one solo maintainer. Read [the documentation router](docs/README.md) before changing domain behavior, provider scope, generated state, publication, or release automation.

## Authority ladder

Use the smallest executable owner that answers the question:

1. `catalog/`, `schemas/`, `app/classification.py`, `app/providers/registry.py`, and `app/site_registry.py` own taxonomy, contracts, provider membership, and site membership.
2. `app/cli.py` owns the application command surface.
3. `docs/reference/` owns maintained rules and intent that cannot be expressed by a schema.
4. `docs/decisions/` owns accepted rationale; ADRs are append-only after acceptance.
5. `docs/operations/` owns repeatable procedures, not domain facts.
6. `docs/providers/` combines generated inventory facts with maintained source judgment.
7. `docs/archive/` is frozen historical context and MUST NOT be cited as current evidence.

If prose conflicts with executable truth, update or archive the prose in the same change. Never create a second unvalidated status list, provider registry, URL inventory, regex taxonomy, or command list in Markdown.

## Working conventions

- Use `uv run python -m app <subcommand>` in local documentation and examples.
- Run `uv run python scripts/render_docs.py` after changing the source inventory, provider registry, site registry, CLI, or maintained document set.
- Run `uv run python scripts/validate_docs.py --check` before handoff.
- Keep provider-owned generated state under `data/providers/<provider_id>/` and `mirror/providers/<provider_id>/`.
- Keep site-owned publication state under `data/sites/<site_id>/` and `bundles/sites/<site_id>/`.
- Keep `PLAN.md` temporary, untracked, and out of commits.
