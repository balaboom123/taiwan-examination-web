# Source Spec Template

Use this template before implementing a new provider.

Create a copy as:

```text
docs/developer/providers/<provider_id>-spec.md
```

Do not start implementation until the template is filled out well enough that another engineer could review ownership, contracts, workflows, and recovery without reading code.

## Copy-Paste Template

```markdown
# Provider Spec: <provider_id>

## 1. Summary

- provider_id: `<provider_id>`
- status: planned
- owner: `<team or person>`
- target site_id(s): `<site_id>, <site_id>`

## 2. Source Overview

- source name:
- source domain(s):
- source type: public web / authenticated web / API / file dump / other
- source update cadence:
- legal or licensing constraints:
- rate limit or anti-bot constraints:

## 3. Stable Identity Model

- stable source exam identifier:
- stable paper/file identifier:
- year semantics:
- category semantics:
- subject semantics:

## 4. Discovery Model

- discovery entrypoint:
- how available years are enumerated:
- how exams are enumerated:
- expected discovery output shape:
- failure behavior:

## 5. Probe Model

- provider-scoped source manifest path:
- probe granularity: year / exam / file
- cheap change signal:
- expensive validation fallback:
- `should_sync` decision rules:

## 6. Raw Data Contract

- raw exam page path:
- required raw fields:
- attachment fields:
- paper fields:
- fields intentionally preserved from source:

## 7. Download And Mirror Model

- mirror root:
- mirror key structure:
- expected file types:
- validation rules:
- stale file cleanup rules:
- checksum policy:

## 8. Normalization Contract

- normalized output path:
- canonical grouping key:
- canonical naming strategy:
- alias ownership:
- review queue path:
- failure log path:
- provider-specific fields that MUST NOT leak into public feeds:

## 9. Publication Integration

- consuming site_id(s):
- bundle selection rules:
- expected bundle cardinality: one canonical bundle / multiple bundles
- bundle inclusion/exclusion rules:
- release tag ownership:
- release tag sharding impact:
- release tag assignment policy:
- compatibility alias asset policy:
- gating behavior:
- frontend/public feed implications:

## 10. CI/CD Plan

- provider sync workflow:
- provider audit workflow:
- discovery workflow:
- site publish workflow changes:
- site deploy workflow changes:
- required secrets:

## 11. Operator Runbook

- standard sync command(s):
- standard audit command(s):
- standard recovery command(s):
- verification steps:
- expected generated outputs:

## 12. Recovery Scenarios

- source unavailable:
- source schema drift:
- invalid payload or HTML placeholder:
- release mismatch:
- gating refresh failure:

## 13. Testing Plan

- parser tests:
- manifest tests:
- publication/feed tests:
- operator verification commands:

## 14. Migration Notes

- does this provider require dual-write compatibility outputs?
- does it force any contract changes?
- does it require frontend changes?
- does it require release script changes?
- does it change the consuming site's release shard count or balancing policy?

## 15. Open Questions

- unresolved technical questions:
- unresolved operational questions:
- unresolved product or ownership questions:
```

## Required Review Questions

Every filled provider spec SHOULD answer these before implementation starts:

- Is `provider_id` stable and well named?
- Are provider-owned and site-owned files clearly separated?
- Can the source be probed cheaply enough for scheduled maintenance?
- Are payload validation rules strict enough to reject source placeholders?
- Can operators run and recover the provider without code spelunking?
- Does the provider require a new site, or can an existing site consume it safely?
- Are secrets and external dependencies documented?

## Approval Gate

A provider spec is ready for implementation only when:

- ownership is clear
- contracts are clear
- workflow ownership is clear
- operator procedures are clear
- recovery paths are clear
- required docs to update are listed

If any of those are missing, the source is not ready to implement.
