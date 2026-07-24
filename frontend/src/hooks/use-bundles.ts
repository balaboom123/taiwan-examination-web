import { useState, useEffect } from "react"
import type { Bundle, BundlePart } from "@/types"
import { classifyBundle } from "@/lib/exam-classification"

interface UseBundlesResult {
  bundles: Bundle[]
  loading: boolean
  error: string | null
}

interface RawBundle {
  id: string
  name: string
  years: number[]
  fileCount: number
  url: string
  parts?: BundlePart[]
  examClass?: string
  examSubclass?: string
  domainId?: string
  examFamilyId?: string
  seriesId?: string
  levelId?: string
  trackId?: string
  variantIds?: string[]
  stageId?: string
  searchAliases?: string[]
  subjectLabels?: string[]
}

function isValidRawBundle(item: unknown): item is RawBundle {
  if (typeof item !== "object" || item === null) return false
  const obj = item as Record<string, unknown>
  return (
    typeof obj.id === "string" &&
    typeof obj.name === "string" &&
    Array.isArray(obj.years) &&
    typeof obj.fileCount === "number" &&
    typeof obj.url === "string" &&
    (obj.searchAliases === undefined || (Array.isArray(obj.searchAliases) && obj.searchAliases.every((item) => typeof item === "string"))) &&
    (obj.subjectLabels === undefined || (Array.isArray(obj.subjectLabels) && obj.subjectLabels.every((item) => typeof item === "string"))) &&
    (obj.parts === undefined || (Array.isArray(obj.parts) && obj.parts.every((part) =>
      typeof part === "object" && part !== null &&
      typeof (part as { label?: unknown }).label === "string" &&
      typeof (part as { url?: unknown }).url === "string" &&
      typeof (part as { fileCount?: unknown }).fileCount === "number"
    )))
  )
}

function enrichBundle(raw: RawBundle): Bundle {
  const fallback = classifyBundle(raw.id, raw.name)
  const examClass = raw.examClass ?? fallback.examClass
  const examSubclass = raw.examSubclass ?? fallback.examSubclass
  return { ...raw, examClass, examSubclass }
}

function normalizeBundlesPayload(data: unknown): unknown[] {
  if (Array.isArray(data)) return data
  if (typeof data !== "object" || data === null) {
    throw new Error("Invalid data format")
  }

  const bundles = (data as { bundles?: unknown }).bundles
  if (!Array.isArray(bundles)) {
    throw new Error("Invalid data format")
  }
  return bundles
}

export function useBundles(): UseBundlesResult {
  const [bundles, setBundles] = useState<Bundle[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const controller = new AbortController()
    const url = `${import.meta.env.BASE_URL}data/bundles.json`

    fetch(url, { signal: controller.signal })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json() as Promise<unknown>
      })
      .then((data) => {
        const bundlesData = normalizeBundlesPayload(data)
        const valid = bundlesData.filter(isValidRawBundle).map(enrichBundle)
        if (valid.length === 0 && bundlesData.length > 0) {
          throw new Error("Data schema mismatch")
        }
        setBundles(valid)
        setLoading(false)
      })
      .catch((err) => {
        if (err.name !== "AbortError") {
          setError(err.message)
          setLoading(false)
        }
      })

    return () => controller.abort()
  }, [])

  return { bundles, loading, error }
}
