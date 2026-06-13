import { readFile } from "node:fs/promises"

function normalizeBasePath(basePath) {
  if (!basePath || basePath === "/") {
    return "/"
  }

  const trimmed = String(basePath).trim()
  if (!trimmed) {
    return "/"
  }

  const withLeadingSlash = trimmed.startsWith("/") ? trimmed : `/${trimmed}`
  return withLeadingSlash.endsWith("/") ? withLeadingSlash : `${withLeadingSlash}/`
}

export function resolvePagesBase({ githubRepository, explicitBase } = {}) {
  if (explicitBase) {
    return normalizeBasePath(explicitBase)
  }

  const repoName = githubRepository?.split("/")[1]
  return repoName ? normalizeBasePath(repoName) : "/"
}

function normalizeBooleanFlag(value) {
  if (value === undefined || value === null || value === "") {
    return undefined
  }

  const normalized = String(value).trim().toLowerCase()
  if (["1", "true", "yes", "on"].includes(normalized)) {
    return true
  }

  if (["0", "false", "no", "off"].includes(normalized)) {
    return false
  }

  throw new TypeError(`Boolean flag must be one of true/false, 1/0, yes/no, or on/off. Received: ${value}`)
}

export function resolveAdsenseEnabled({ githubRepository, explicitBase, explicitEnabled, isBuild = true } = {}) {
  const enabledOverride = normalizeBooleanFlag(explicitEnabled)
  if (enabledOverride !== undefined) {
    return enabledOverride
  }

  if (!isBuild) {
    return false
  }

  return resolvePagesBase({ githubRepository, explicitBase }) === "/"
}

function toFrontendBundle(bundle, index) {
  if (typeof bundle !== "object" || bundle === null) {
    throw new TypeError(`Bundle at index ${index} must be an object`)
  }

  const {
    canonical_id: id,
    canonical_name: name,
    years,
    file_count: fileCount,
    download_url: url,
  } = bundle

  if (typeof id !== "string" || typeof name !== "string" || !Array.isArray(years) || typeof fileCount !== "number" || typeof url !== "string") {
    throw new TypeError(`Bundle at index ${index} does not match the generated data schema`)
  }

  return {
    id,
    name,
    years,
    fileCount,
    url,
  }
}

export function toFrontendBundles(bundles) {
  if (!Array.isArray(bundles)) {
    throw new TypeError("Generated bundles data must be an array")
  }

  return bundles.map((bundle, index) => toFrontendBundle(bundle, index))
}

export async function readFrontendBundlesSource(sourcePath) {
  const sourceText = await readFile(sourcePath, "utf8")
  return JSON.stringify(toFrontendBundles(JSON.parse(sourceText)))
}
