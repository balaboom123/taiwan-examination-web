import assert from "node:assert/strict"
import test from "node:test"

import { toFrontendBundles } from "./bundles-data.mjs"

test("frontend feed preserves searchable aliases and subject labels", () => {
  const [bundle] = toFrontendBundles([
    {
      bundle_id: "wdasec-skill-skill-certification-class-c-example",
      canonical_name: "全國技術士技能檢定｜丙級",
      years: [115],
      file_count: 2,
      download_url: "https://example.com/skill.zip",
      checksum: "sha-1",
      domain_id: "certification",
      exam_family_id: "skill-certification",
      exam_series_id: "skill-certification",
      level_id: "class-c",
      track_id: "skill-example",
      variant_ids: [],
      stage_id: "not-applicable",
      search_aliases: ["冷凍空調裝修"],
      subject_labels: ["冷凍空調裝修"],
    },
  ])

  assert.equal(bundle.name, "全國技術士技能檢定｜丙級")
  assert.deepEqual(bundle.searchAliases, ["冷凍空調裝修"])
  assert.deepEqual(bundle.subjectLabels, ["冷凍空調裝修"])
})
