# Concepts

These terms are stable repository concepts. Serialized field definitions remain authoritative in `schemas/` and `catalog/`.

| Concept | Meaning | Stable identifier or owner |
| --- | --- | --- |
| provider | One official-source ingestion implementation. It discovers, fetches, validates, normalizes, and records failures without owning public presentation. | `provider_id`; `app/providers/registry.py` |
| site | A public projection over one or more providers, with publication thresholds, release topology, and frontend behavior. | `site_id`; `app/site_registry.py` |
| source event | A provider-owned exam occurrence or listing whose source identity must remain reproducible. | `source_exam_id` within a provider |
| paper | One normalized downloadable source record associated with an event, subject, kind, and source URL. | normalized-paper schema |
| canonical identity | The deterministic classification used to group equivalent records without depending on presentation names alone. | `canonical_id`; identity catalog and classifier |
| bundle | A site-selected archive of papers that satisfies one pure canonical identity and the publication contract. | `bundle_id`; bundle schema |
| release shard | A deterministic site-owned GitHub release tag containing a bounded subset of bundle assets. Providers do not own shards. | `release_tag`; release plan schema |
| source inventory | Reviewed scope, source URLs, disposition, availability, observed local counts, restrictions, and evidence for providers and investigated candidates. | `catalog/source-inventory.json` |
| source manifest | Provider-owned discovery snapshot used to compare official event availability with retained state. It is generated state, not the reviewed scope inventory. | `data/providers/<provider_id>/source-manifest.json` |
| publication | The transformation from provider state into site bundles, release-asset metadata, and the frontend feed. | `app/publisher.py` and site paths |
| quarantine | An explicit site publication exclusion for records that must remain retained but cannot be published safely. | `catalog/mappings/publication-quarantine.json` |

The important boundary is provider versus site: ingestion state stays provider-owned, while bundles, release tags, and frontend feeds stay site-owned.
