# Catalog audit and release preflight

Status: current operator procedure  
Owner: release and data operators

This procedure checks all providers configured for a site. It is not a 一般行政-only report.

## Read-only audit

From the repository root:

~~~bash
python3 -m app audit-catalog --site-id default --output .tmp/catalog-audit.json
~~~

The command loads every provider state, recomputes v2 identity for every normalized paper, compares identities with current site bundles, and writes a machine-readable report. It does not download source files or mutate provider/site data.

The report includes provider and paper counts, per-provider confidence and signatures, review records, mixed legacy groups, current bundle dispositions, physical asset counts by release tag, the 1,000-asset hard limit, the 900-asset safety target, projected public v2 bundle count, physical projected shard counts (including aliases), and coverage.

For triage:

~~~bash
python3 - <<PY
import json
from pathlib import Path
report = json.loads(Path(".tmp/catalog-audit.json").read_text())
for key in (
    "paper_records_scanned", "provider_count", "records_needing_review",
    "current_bundle_disposition_counts", "current_release_asset_counts",
    "current_release_capacity_ok", "planned_bundle_count", "planned_release_shards",
):
    print(key, report[key])
PY
~~~

## Event coverage audit

Run the event-level audit separately from the identity audit:

~~~bash
python3 -m app history-audit --site-id default --output .tmp/history-audit.json
python3 -m app history-audit --site-id default --strict --output .tmp/history-audit-strict.json
~~~

The report distinguishes download gaps, normalization gaps, normalized-but-not-published events, source-only parser gaps, and excluded-by-publication-policy events. The strict form fails on unresolved gaps and passes only when every excluded event has an explicit site-policy disposition.

The strict form is a gate:

~~~bash
python3 -m app audit-catalog --strict --output .tmp/catalog-audit-strict.json
~~~

It returns non-zero while any public record lacks an approved identity disposition or coverage fails. A review-confidence record is acceptable only when it has an event-specific review bundle and a matching evidence-queue signature; the report exposes these as `approved_review_isolated_records`. Resolve or explicitly document any `unapproved_review_records`; do not add a fallback merely to make the command green.

## Migration

After mapping changes are reviewed:

~~~bash
python3 -m app migrate-catalog --site-id default
~~~

This rewrites all retained provider paper files for the configured site into v2 fields without network access. Use --provider for a focused iteration, then always run the complete command before publication. Raw pages, source IDs, legacy canonical IDs, failures, and compatibility fields are preserved.

Inspect the diff and rerun the audit. A mapping change is incomplete until every historical year is reclassified.

## Bundle and site publication

A local publication rebuilds the site projection:

~~~bash
python3 -m app publish-site --site-id default --repository OWNER/REPOSITORY
~~~

Publication reclassifies loaded state, plans bundles by v2 identity, assigns release shards, validates physical capacity, and writes site-scoped bundles/release/frontend feeds. It needs local mirror/bundle inputs and does not authorize remote upload.

Before building a large archive, use the audit projection. Keep each tag at or below 900 physical ZIP names; compatibility names in legacy_asset_names count too.

For a read-only shard assignment from the current site inventory, use the v2 namespace (no upload or deletion occurs):

~~~bash
python3 -m app plan-release --site-id default --output .tmp/release-plan.json
~~~

The plan reports primary and compatibility asset names per tag. It defaults to default-bundles-v2 so an over-cap legacy v1 tag can be migrated without preserving its old assignment.

## Review workflow

For each review item:

1. open the raw provider record and source event;
2. inspect the provider official hierarchy and historical terminology;
3. add a narrow, time-bounded mapping or explicit exclusion under catalog/mappings/;
4. add a fixture and test;
5. rerun migration and the whole audit;
6. record rationale in an ADR when bundle identity changes.

If the source never publishes a reliable level, use explicit provider-specific not-applicable or an isolated review bundle and document why. Do not close review by deleting the record or assigning it to an unrelated track.

## Release upload safety

Before any authorized remote operation:

1. compare local inventory with actual remote names;
2. ensure each tag is below the safety target;
3. check duplicate names and aliases;
4. upload only planned v2 inventory;
5. verify remote coverage;
6. do not prune v1 assets during migration.

The helper refuses a tag over 1,000. A pre-existing over-cap v1 inventory is a migration finding, not permission to delete assets.

## Recovery

If publication fails capacity validation, keep provider state and v1 assets intact. Reduce physical aliases, add a v2 shard, or revise the plan; do not merge distinct bundles. If a v2 bundle is wrong, restore the prior local site feed or rebuild from preserved v1 state. Remote rollback is a separate approved operation.

