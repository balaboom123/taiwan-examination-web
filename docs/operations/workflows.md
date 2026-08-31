# Workflow ownership

Workflow filenames are implementation details; ownership determines what they may change.

| Workflow class | Scope | May write |
| --- | --- | --- |
| provider discovery/sync | one named provider | provider state, provider mirror, scoped publication inputs |
| audit | repository or selected providers/sites | reports and explicitly reviewed generated corrections |
| site publication/release | one named site | site bundles, feeds, release plans, and assigned assets |
| deploy | one named site | frontend build and deployment output |
| CI | checked-in repository | no persistent runtime state |

Provider workflows must not invent site release ownership. Site workflows must not parse official sources or mutate provider identity. Deploy workflows consume site feeds rather than raw provider crawl state.

## Sync floor guard

`.github/scripts/commit-and-push.sh` runs `scripts/check_sync_floor.py` before committing generated provider data. The guard resolves provider IDs from staged `data/providers/<provider_id>/` paths and refuses event or paper counts below the reviewed `local_state` floor in `catalog/source-inventory.json`. Source growth is allowed. A genuine reviewed removal requires updating the inventory floor; a transiently truncated sync must be rerun.

## Health reporting

`workflow-health` reacts to every scheduled workflow and the Pages deployment.
The first failure or timeout opens one labelled issue; repeated failures keep
that issue open without adding notification comments, and a later success
closes it. Cancelled runs are ignored because deployment concurrency cancels
superseded work intentionally.

The daily staleness pass uses each workflow's schedule to choose its window and
accepts a successful manual rerun as recovery. Health reactions are not placed
in one global concurrency group: GitHub retains only one pending run per group,
which can discard completion events when several provider workflows finish
together.

Manual diagnosis uses:

```bash
uv run python scripts/check_sync_floor.py --repo-root . -- data/providers/<provider_id>/papers/<year>.json
```

## Change checklist

When adding or changing a workflow:

1. Name its provider or site owner explicitly.
2. Use scoped provider and site paths.
3. Keep permissions least-privileged and secrets limited to the step that needs them.
4. Preserve strict catalog, source-inventory, publication, history, release-plan, and documentation gates.
5. Add or update `tests/test_workflows.py` for structural workflow contracts.
6. Update the [runbook](runbook.md) and [recovery guide](recovery.md) when operator behavior changes.

Use [CI/CD and release](ci-cd-and-release.md) for gate and release topology details.
