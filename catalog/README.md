# Catalog sources of truth

This directory contains reviewed, versioned domain knowledge used to classify exam records. It is not generated crawl state.

## Layout

- taxonomy/exam-identity-v2.json: shared domains, families, series, levels, and policy metadata.
- mappings/moex/level-rules.json: MOEX level, promotion, qualification, and historical marker rules.
- mappings/provider-policies.json: provider-specific publication and minimum-history policy.
- mappings/<provider>/: future provider-specific mappings when shared rules are insufficient.

## Change protocol

Every concept or rule change must include:

- stable ID and human label;
- provider and effective date/year range when applicable;
- evidence or source reference;
- reason the dimension affects paper identity;
- a fixture/test or audit signature proving the intended result;
- catalog version impact.

IDs are keys. Labels and aliases may change without renaming an ID. Do not put generated paper/bundle JSON or source downloads here.

The classifier may contain a small deterministic rule that cannot be expressed as data, but catalog remains the reviewable vocabulary. A change that can alter historical bundles requires full migrate-catalog and audit-catalog runs.

