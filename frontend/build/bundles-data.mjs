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
    search_aliases: searchAliases,
    subject_labels: subjectLabels,
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
      ...(Array.isArray(searchAliases) && searchAliases.length > 0 ? { searchAliases } : {}),
      ...(Array.isArray(subjectLabels) && subjectLabels.length > 0 ? { subjectLabels } : {}),
    })
  }
  return frontendBundle
}

export function toFrontendBundles(bundles) {
  const normalizedBundles = normalizeBundlesSource(bundles)
  const grouped = new Map()

  normalizedBundles.forEach((bundle, index) => {
    const frontend = toFrontendBundle(bundle, index)
    const partCount = Number.isInteger(bundle.part_count) ? bundle.part_count : 1
    const partIndex = Number.isInteger(bundle.part_index) ? bundle.part_index : 1
    const part = {
      label: typeof bundle.part_label === "string" && bundle.part_label
        ? bundle.part_label
        : `第 ${partIndex}/${partCount} 部分`,
      url: frontend.url,
      fileCount: frontend.fileCount,
    }
    const existing = grouped.get(frontend.id)
    if (!existing) {
      if (partCount > 1) frontend.parts = [part]
      grouped.set(frontend.id, frontend)
      return
    }

    existing.years = Array.from(new Set([...existing.years, ...frontend.years])).sort((a, b) => b - a)
    existing.fileCount += frontend.fileCount
    for (const field of ["searchAliases", "subjectLabels"]) {
      const values = Array.isArray(frontend[field]) ? frontend[field] : []
      if (values.length > 0) {
        existing[field] = Array.from(new Set([...(existing[field] ?? []), ...values]))
      }
    }
    if (!existing.parts) existing.parts = []
    existing.parts.push(part)
  })

  return Array.from(grouped.values()).map((bundle) => {
    if (bundle.parts && bundle.parts.length <= 1) delete bundle.parts
    return bundle
  })
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
