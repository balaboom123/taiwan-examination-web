import { useState, useEffect } from "react"
import type { Bundle } from "@/types"

interface UseBundlesResult {
  bundles: Bundle[]
  loading: boolean
  error: string | null
}

function isValidBundle(item: unknown): item is Bundle {
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
        if (!Array.isArray(data)) throw new Error("Invalid data format")
        const valid = data.filter(isValidBundle)
        if (valid.length === 0 && data.length > 0) {
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
