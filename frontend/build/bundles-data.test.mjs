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
