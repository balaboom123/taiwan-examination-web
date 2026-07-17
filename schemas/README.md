# Versioned JSON contracts

Schemas here validate persisted v2 boundaries. They are separate from taxonomy data and generated runtime state.

- taxonomy.schema.json: shared identity dimensions and bundle-purity source.
- provider-mapping.schema.json: provider rule and review-policy source.
- normalized-paper-v2.schema.json: provider paper records with identity facets and provenance.
- bundle-v2.schema.json: site bundle inventory entries and ZIP manifest metadata.
- frontend-bundle-feed-v2.schema.json: public structured feed consumed by the frontend.
- release-plan-v2.schema.json: dry-run shard assignments and physical asset counts.
- classification-audit.schema.json: whole-catalog audit output.

A v2 payload must declare schema_version 2 and catalog_version exam-identity-v2 where required. Consumers should reject unsupported versions instead of guessing.

At minimum, validate syntax:

~~~bash
for file in schemas/*.json catalog/taxonomy/*.json catalog/mappings/**/*.json; do
  python3 -m json.tool "$file" >/dev/null
done
~~~

JSON Schema validation should be added to CI with the repository chosen validator. Stdlib parsing checks syntax only.

