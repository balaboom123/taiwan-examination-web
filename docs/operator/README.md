# Operator Documentation

This section is the user-facing documentation for repo operators and maintainers.

Use these docs if you:

- run syncs manually
- trigger or inspect GitHub Actions workflows
- rebuild bundles or site outputs
- refresh LootLabs links
- investigate publication failures

These docs assume you are operating the repository, not browsing the public website.

## Reading Order

1. `runbook.md`
2. `workflows.md`
3. `recovery.md`

## Safety Rules

- Prefer probe or targeted refresh before a full rebuild.
- Treat `data/`, `site/`, `bundles/`, and `mirror/` as operational state.
- Do not manually edit generated files unless the recovery doc explicitly calls for it.
- Remember that `data/aliases.json` is a manual input; most other `data/` files are generated outputs.

## Current Status

Current operating model:

- one active provider: MOEX
- one primary release tag for bundles
- one current gating provider: LootLabs
- legacy `site/` output plus modern `frontend/` deploy

Future operating model:

- multiple providers
- potentially multiple sites
- provider-scoped sync and recovery
- site-scoped release and deploy paths
