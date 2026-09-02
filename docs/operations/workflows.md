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

## Generated-state commit guard

`.github/scripts/commit-and-push.sh` runs `scripts/check_sync_floor.py` and
`scripts/validate_publication.py` before committing generated data. The floor
guard resolves provider IDs from staged `data/providers/<provider_id>/` paths
and refuses event or paper counts below the reviewed `local_state` floor in
`catalog/source-inventory.json`. The publication preflight rejects unresolved
sync failures, discovery-manifest drift, and provider/site eligibility drift.
This is required because pushes made with `GITHUB_TOKEN` do not start the
normal push CI workflow. Source growth is allowed only while the resulting
tree remains deployable. A genuine reviewed removal requires updating the
inventory floor; a transiently incomplete sync must be rerun.

A failed sync may write partial state inside its runner so the shared guard can
diagnose it, but that state is not committed to `main`. The failed Actions run
and, for scheduled workflows, its single workflow-health issue retain the
operational evidence while the last deployable provider state stays checked in. Pages ignores failed upstream
workflow runs; a successful sync or the daily Pages backstop still exercises
the full deployment gates.

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
