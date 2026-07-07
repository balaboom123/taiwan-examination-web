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

export function normalizeBundlesSource(source) {
  if (Array.isArray(source)) {
    return source
  }

  if (source && typeof source === "object" && Array.isArray(source.bundles)) {
    return source.bundles
  }

  throw new TypeError("Generated bundles data must be an array or wrapped site bundles object")
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
    download_url: rawUrl,
    checksum,
  } = bundle

  if (
    typeof id !== "string" ||
    typeof name !== "string" ||
    !Array.isArray(years) ||
    typeof fileCount !== "number" ||
    typeof rawUrl !== "string" ||
    typeof checksum !== "string"
  ) {
    throw new TypeError(`Bundle at index ${index} does not match the generated data schema`)
  }

  return {
    id,
    name,
    years,
    fileCount,
    url: rawUrl,
  }
}

export function toFrontendBundles(bundles) {
  const normalizedBundles = normalizeBundlesSource(bundles)
  return normalizedBundles.map((bundle, index) => toFrontendBundle(bundle, index))
}

function normalizePathCandidates(pathOrPaths) {
  return Array.isArray(pathOrPaths) ? pathOrPaths : [pathOrPaths]
}

async function readFirstAvailableText(pathOrPaths) {
  const [candidatePath] = normalizePathCandidates(pathOrPaths)
  try {
    return await readFile(candidatePath, "utf8")
  } catch (error) {
    if (error && typeof error === "object" && error.code === "ENOENT") {
      throw error
    }
    throw error
  }
}

export async function readFrontendBundlesSource(sourcePath) {
  const sourceText = await readFirstAvailableText(sourcePath)

  return JSON.stringify(toFrontendBundles(JSON.parse(sourceText)))
}
