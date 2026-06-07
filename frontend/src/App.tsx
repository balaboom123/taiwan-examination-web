import { useState, useMemo } from "react"
import { useBundles } from "@/hooks/use-bundles"
import { useDebouncedValue } from "@/hooks/use-debounce"
import { rocToAd } from "@/lib/utils"
import { Header } from "@/components/header"
import { SearchBar } from "@/components/search-bar"
import { YearFilter } from "@/components/year-filter"
import { SortSelect, type SortKey } from "@/components/sort-select"
import { BundleCard } from "@/components/bundle-card"
import { StatsBar } from "@/components/stats-bar"
import { EmptyState } from "@/components/empty-state"
import { LoadingSkeleton } from "@/components/loading-skeleton"
import { Pagination } from "@/components/pagination"
import { AlertTriangle } from "lucide-react"
import type { Bundle } from "@/types"

const PAGE_SIZE = 30

function App() {
  const { bundles, loading, error } = useBundles()
  const [query, setQuery] = useState("")
  const debouncedQuery = useDebouncedValue(query, 200)
  const [selectedYear, setSelectedYear] = useState<number | null>(null)
  const [sortKey, setSortKey] = useState<SortKey>("name")
  const [page, setPage] = useState(1)

  const allYears = useMemo(() => {
    const set = new Set<number>()
    for (const b of bundles) {
      for (const y of b.years) set.add(y)
    }
    return Array.from(set).sort((a, b) => b - a)
  }, [bundles])

  const filtered = useMemo(() => {
    let result = bundles

    if (debouncedQuery.trim()) {
      const q = debouncedQuery.trim().toLowerCase()
      result = result.filter((b) => b.name.toLowerCase().includes(q))
    }

    if (selectedYear !== null) {
      result = result.filter((b) => b.years.includes(selectedYear))
    }

    const sorted = [...result]
    switch (sortKey) {
      case "name":
        sorted.sort((a, b) => a.name.localeCompare(b.name, "zh-TW"))
        break
      case "files-desc":
        sorted.sort((a, b) => b.fileCount - a.fileCount)
        break
      case "years-desc":
        sorted.sort((a, b) => b.years.length - a.years.length)
        break
    }

    return sorted
  }, [bundles, debouncedQuery, selectedYear, sortKey])

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE))
  const safePage = Math.min(page, totalPages)
  const paginated = filtered.slice(
    (safePage - 1) * PAGE_SIZE,
    safePage * PAGE_SIZE
  )

  const totalFiles = useMemo(
    () => bundles.reduce((sum, b) => sum + b.fileCount, 0),
    [bundles]
  )

  const yearRange = useMemo(() => {
    if (allYears.length === 0) return ""
    const newest = allYears[0]
    const oldest = allYears[allYears.length - 1]
    return `${oldest}–${newest} (${rocToAd(oldest)}–${rocToAd(newest)})`
  }, [allYears])

  function handleQueryChange(value: string) {
    setQuery(value)
    setPage(1)
  }

  function handleYearChange(year: number | null) {
    setSelectedYear(year)
    setPage(1)
  }

  function handleSortChange(key: SortKey) {
    setSortKey(key)
    setPage(1)
  }

  function handleReset() {
    setQuery("")
    setSelectedYear(null)
    setPage(1)
  }

  if (error) {
    return (
      <div className="min-h-[100dvh] flex flex-col">
        <Header totalBundles={0} />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="size-14 rounded-2xl bg-red-50 flex items-center justify-center mx-auto mb-4">
              <AlertTriangle className="size-7 text-red-400" strokeWidth={1.5} />
            </div>
            <p className="text-base font-medium text-stone-900">
              資料載入失敗
            </p>
            <p className="mt-1 text-sm text-stone-500">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-4 h-9 px-4 rounded-lg text-sm font-medium bg-stone-100 text-stone-700 hover:bg-stone-200 transition-colors"
            >
              重新載入
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-[100dvh] flex flex-col">
      <Header totalBundles={bundles.length} />

      <main className="flex-1 max-w-6xl mx-auto w-full px-6 py-8">
        <div className="mb-8 animate-fade-up">
          <h2 className="text-2xl md:text-3xl font-bold font-[Outfit] tracking-tight text-stone-900 leading-tight">
            歷屆考試試題下載
          </h2>
          <p className="mt-2 text-sm text-stone-500 max-w-[65ch]">
            收錄考選部歷年各類國家考試試題，依類科分類打包為 ZIP 檔案，可直接下載。
          </p>
        </div>

        {!loading && (
          <div className="mb-6 animate-fade-up" style={{ animationDelay: "60ms" }}>
            <StatsBar
              total={bundles.length}
              totalFiles={totalFiles}
              yearRange={yearRange}
            />
          </div>
        )}

        <div
          className="flex flex-col gap-4 mb-6 animate-fade-up"
          style={{ animationDelay: "120ms" }}
        >
          <SearchBar value={query} onChange={handleQueryChange} />

          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <YearFilter
              years={allYears}
              selected={selectedYear}
              onSelect={handleYearChange}
            />
            <SortSelect value={sortKey} onChange={handleSortChange} />
          </div>
        </div>

        {loading ? (
          <LoadingSkeleton />
        ) : filtered.length === 0 ? (
          <EmptyState onReset={handleReset} />
        ) : (
          <>
            <div className="mb-3 text-sm text-stone-400" aria-live="polite">
              顯示 {(safePage - 1) * PAGE_SIZE + 1}–
              {Math.min(safePage * PAGE_SIZE, filtered.length)} / 共{" "}
              <span className="font-mono">{filtered.length}</span> 筆
            </div>
            <div className="flex flex-col gap-3">
              {paginated.map((bundle: Bundle, index: number) => (
                <div
                  key={bundle.id}
                  className="animate-fade-up"
                  style={{ animationDelay: `${index * 30}ms` }}
                >
                  <BundleCard bundle={bundle} />
                </div>
              ))}
            </div>
            <Pagination
              current={safePage}
              total={totalPages}
              onChange={setPage}
            />
          </>
        )}
      </main>

      <footer className="border-t border-stone-200 mt-auto">
        <div className="max-w-6xl mx-auto px-6 py-5 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between text-xs text-stone-400">
          <span>
            資料來源：考選部歷屆試題查詢
          </span>
          <a
            href="https://github.com/balaboom123/taiwan_examination_web"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-stone-600 transition-colors"
          >
            GitHub
          </a>
        </div>
      </footer>
    </div>
  )
}

export default App
