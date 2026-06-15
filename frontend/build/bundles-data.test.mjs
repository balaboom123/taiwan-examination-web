import assert from "node:assert/strict"
import test from "node:test"

import { resolveAdsenseEnabled, resolvePagesBase, toFrontendBundles } from "./bundles-data.mjs"

test("resolvePagesBase uses the renamed GitHub repository path", () => {
  assert.equal(
    resolvePagesBase({ githubRepository: "balaboom123/taiwan-examination-web" }),
    "/taiwan-examination-web/",
  )
})

test("resolvePagesBase falls back to the site root outside GitHub Pages builds", () => {
  assert.equal(resolvePagesBase({}), "/")
})

test("resolveAdsenseEnabled disables AdSense for GitHub Pages project-site builds", () => {
  assert.equal(
    resolveAdsenseEnabled({ githubRepository: "balaboom123/taiwan-examination-web" }),
    false,
  )
})

test("resolveAdsenseEnabled enables AdSense for root-hosted production builds", () => {
  assert.equal(resolveAdsenseEnabled({ explicitBase: "/" }), true)
})

test("resolveAdsenseEnabled stays off during non-build runs unless explicitly enabled", () => {
  assert.equal(resolveAdsenseEnabled({ isBuild: false }), false)
  assert.equal(resolveAdsenseEnabled({ isBuild: false, explicitEnabled: "true" }), true)
})

test("toFrontendBundles converts generated bundle records into the frontend schema", () => {
  assert.deepEqual(
    toFrontendBundles([
      {
        canonical_id: "nurse",
        canonical_name: "Nurse",
        years: [115, 113],
        file_count: 607,
        download_url: "https://example.com/nurse.zip",
      },
    ]),
    [
      {
        id: "nurse",
        name: "Nurse",
        years: [115, 113],
        fileCount: 607,
        url: "https://example.com/nurse.zip",
      },
    ],
  )
})

test("toFrontendBundles replaces raw bundle urls with LootLabs urls", () => {
  assert.deepEqual(
    toFrontendBundles(
      [
        {
          canonical_id: "nurse",
          canonical_name: "Nurse",
          years: [115],
          file_count: 1,
          download_url: "https://github.com/example/repo/releases/download/moex-bundles/nurse.zip",
        },
      ],
      {
        lootlabsManifest: {
          version: 1,
          provider: "lootlabs",
          settings: { tier_id: 1, number_of_tasks: 1, theme: 1 },
          bundles: {
            nurse: {
              canonical_id: "nurse",
              asset_name: "nurse.zip",
              loot_url: "https://loot-link.com/s?cached",
              target_download_url: "https://github.com/example/repo/releases/download/moex-bundles/nurse.zip",
              target_checksum: "sha-1",
              updated_at: "2026-06-15T08:00:00+08:00",
            },
          },
        },
      },
    ),
    [
      {
        id: "nurse",
        name: "Nurse",
        years: [115],
        fileCount: 1,
        url: "https://loot-link.com/s?cached",
      },
    ],
  )
})

test("toFrontendBundles throws when a bundle has no LootLabs manifest entry", () => {
  assert.throws(
    () =>
      toFrontendBundles(
        [
          {
            canonical_id: "nurse",
            canonical_name: "Nurse",
            years: [115],
            file_count: 1,
            download_url: "https://github.com/example/repo/releases/download/moex-bundles/nurse.zip",
          },
        ],
        {
          lootlabsManifest: {
            version: 1,
            provider: "lootlabs",
            settings: { tier_id: 1, number_of_tasks: 1, theme: 1 },
            bundles: {},
          },
        },
      ),
    /Missing LootLabs link for bundle nurse/,
  )
})

test("toFrontendBundles throws when a LootLabs manifest entry has no loot_url", () => {
  assert.throws(
    () =>
      toFrontendBundles(
        [
          {
            canonical_id: "nurse",
            canonical_name: "Nurse",
            years: [115],
            file_count: 1,
            download_url: "https://github.com/example/repo/releases/download/moex-bundles/nurse.zip",
          },
        ],
        {
          lootlabsManifest: {
            version: 1,
            provider: "lootlabs",
            settings: { tier_id: 1, number_of_tasks: 1, theme: 1 },
            bundles: {
              nurse: {
                canonical_id: "nurse",
                asset_name: "nurse.zip",
                loot_url: "",
                target_download_url: "https://github.com/example/repo/releases/download/moex-bundles/nurse.zip",
                target_checksum: "sha-1",
                updated_at: "2026-06-15T08:00:00+08:00",
              },
            },
          },
        },
      ),
    /Invalid LootLabs entry for bundle nurse/,
  )
})
