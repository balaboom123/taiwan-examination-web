# Operator documentation

This section is for repository operators and maintainers running syncs, audits, publication, release, deployment, and recovery.

The identity and release migration adds whole-catalog audit and v2 shard preflight. Read catalog-audit.md before changing taxonomy, migration, bundles, or releases.

## Reading order

1. catalog-audit.md
2. runbook.md
3. workflows.md
4. recovery.md

## Safety rules

- Prefer probe or targeted refresh before a full rebuild.
- Treat data/, bundles/, and mirror/ as operational state.
- Do not manually edit generated files unless recovery explicitly requires it.
- Maintain taxonomy and mappings under catalog/, not under generated data/.
- Count physical release asset names, including compatibility aliases.
- Do not upload, prune, or delete legacy assets without explicit authorization.

## Current status

The default site registry currently spans all configured providers, although provider state may be populated incrementally. The current v1 inventory is retained for compatibility. V2 publication uses structured identity and may span multiple release shards; each shard targets at most 900 physical assets and must never exceed 1,000.

The modern frontend is fed by site-scoped publication data. Older pages describing one active provider or one release tag are transition snapshots and are subordinate to the current identity reference, ADR, and operator audit procedure.
