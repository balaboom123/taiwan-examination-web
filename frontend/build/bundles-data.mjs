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
    canonical_id: legacyId,
    bundle_id: structuredId,
    canonical_name: canonicalName,
    bundle_name: bundleName,
    years,
    file_count: fileCount,
    download_url: rawUrl,
    checksum,
    domain_id: domainId,
    exam_family_id: examFamilyId,
    exam_series_id: seriesId,
    level_id: levelId,
    track_id: trackId,
    variant_ids: variantIds,
    stage_id: stageId,
    exam_class: examClass,
    exam_subclass: examSubclass,
  } = bundle
  const id = typeof structuredId === "string" && structuredId ? structuredId : legacyId
  const name = typeof bundleName === "string" && bundleName ? bundleName : canonicalName

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

  const frontendBundle = {
    id,
    name,
    years,
    fileCount,
    url: rawUrl,
  }
  if (typeof structuredId === "string" && structuredId) {
    Object.assign(frontendBundle, {
      domainId,
      examFamilyId,
      seriesId,
      levelId,
      trackId,
      variantIds: Array.isArray(variantIds) ? variantIds : [],
      stageId,
      examClass: typeof examClass === "string" ? examClass : undefined,
      examSubclass: typeof examSubclass === "string" ? examSubclass : undefined,
    })
  }
  return frontendBundle
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
