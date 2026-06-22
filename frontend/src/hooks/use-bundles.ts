import { useState, useEffect } from "react"
import type { Bundle } from "@/types"
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
}

function isValidRawBundle(item: unknown): item is RawBundle {
  if (typeof item !== "object" || item === null) return false
  const obj = item as Record<string, unknown>
  return (
    typeof obj.id === "string" &&
    typeof obj.name === "string" &&
    Array.isArray(obj.years) &&
    typeof obj.fileCount === "number" &&
    typeof obj.url === "string"
  )
}

function enrichBundle(raw: RawBundle): Bundle {
  const { examClass, examSubclass } = classifyBundle(raw.id, raw.name)
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
