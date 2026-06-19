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

function normalizeLootlabsManifest(manifest) {
  if (!manifest || typeof manifest !== "object") {
    throw new TypeError("LootLabs manifest is required")
  }

  if (manifest.provider !== "lootlabs" || typeof manifest.bundles !== "object" || manifest.bundles === null) {
    throw new TypeError("LootLabs manifest does not match the expected schema")
  }

  return manifest
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

export function resolveLootlabsEnabled({ explicitEnabled } = {}) {
  return normalizeBooleanFlag(explicitEnabled) ?? false
}

function toFrontendBundle(bundle, index, lootlabsEntries) {
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

  const entry = lootlabsEntries?.[id]
  if (lootlabsEntries) {
    if (!entry) {
      throw new TypeError(`Missing LootLabs link for bundle ${id}`)
    }

    if (typeof entry.loot_url !== "string" || !entry.loot_url) {
      throw new TypeError(`Invalid LootLabs entry for bundle ${id}`)
    }

    if (entry.target_download_url !== rawUrl || entry.target_checksum !== checksum) {
      throw new TypeError(`Invalid LootLabs entry for bundle ${id}`)
    }
  }

  return {
    id,
    name,
    years,
    fileCount,
    url: entry ? entry.loot_url : rawUrl,
  }
}

export function toFrontendBundles(bundles, { lootlabsManifest } = {}) {
  const normalizedBundles = normalizeBundlesSource(bundles)
  const manifest = lootlabsManifest ? normalizeLootlabsManifest(lootlabsManifest) : null
  const lootlabsEntries = manifest?.bundles
  return normalizedBundles.map((bundle, index) => toFrontendBundle(bundle, index, lootlabsEntries))
}

function normalizePathCandidates(pathOrPaths) {
  return Array.isArray(pathOrPaths) ? pathOrPaths : [pathOrPaths]
}

async function readFirstAvailableText(pathOrPaths) {
  let lastMissingError

  for (const candidatePath of normalizePathCandidates(pathOrPaths)) {
    try {
      return await readFile(candidatePath, "utf8")
    } catch (error) {
      if (error && typeof error === "object" && error.code === "ENOENT") {
        lastMissingError = error
        continue
      }
      throw error
    }
  }

  throw lastMissingError ?? new Error("No readable input path was provided")
}

export async function readFrontendBundlesSource(sourcePath, { lootlabsManifestPath } = {}) {
  const [sourceText, manifestText] = await Promise.all([
    readFirstAvailableText(sourcePath),
    lootlabsManifestPath ? readFirstAvailableText(lootlabsManifestPath) : Promise.resolve(undefined),
  ])

  return JSON.stringify(
    toFrontendBundles(JSON.parse(sourceText), {
      lootlabsManifest: manifestText ? JSON.parse(manifestText) : undefined,
    }),
  )
}
