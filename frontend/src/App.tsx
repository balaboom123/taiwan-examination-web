import { useState, useMemo } from "react"
import { useBundles } from "@/hooks/use-bundles"
import { useDebouncedValue } from "@/hooks/use-debounce"
import { formatYearRange } from "@/lib/utils"
import { Header } from "@/components/header"
import { SearchBar } from "@/components/search-bar"
import { YearFilter } from "@/components/year-filter"
import { SortSelect, type SortKey } from "@/components/sort-select"
import { BundleRow } from "@/components/bundle-row"
import { StatsBar } from "@/components/stats-bar"
import { EmptyState } from "@/components/empty-state"
import { LoadingSkeleton } from "@/components/loading-skeleton"
import { Pagination } from "@/components/pagination"
import { Stamp } from "@/components/stamp"
import { CategoryFilter } from "@/components/category-filter"
import { EXAM_CLASSES, type ExamClass } from "@/lib/exam-classification"
import type { Bundle } from "@/types"

const PAGE_SIZE = 30

function PaperGrain() {
  return (
    <div
      aria-hidden="true"
      className="texture-paper pointer-events-none fixed inset-0 z-50 opacity-[0.035] mix-blend-multiply"
    />
  )
}

function Footer() {
  return (
    <footer className="border-t border-line">
      <div className="mx-auto flex max-w-4xl flex-col gap-2 px-6 py-6 text-xs text-ink-500 sm:flex-row sm:items-center sm:justify-between">
        <span>資料來源：考選部 · 國營事業 · 國中會考 · 技能檢定 · 本站為非官方整理</span>
        <a
          href="https://github.com/balaboom123/taiwan-examination-web"
          target="_blank"
          rel="noopener noreferrer"
          className="font-mono transition-colors hover:text-ink-950"
        >
          GitHub
        </a>
      </div>
    </footer>
  )
}

function App() {
  const { bundles, loading, error } = useBundles()
  const [query, setQuery] = useState("")
  const debouncedQuery = useDebouncedValue(query, 200)
  const [selectedYear, setSelectedYear] = useState<number | null>(null)
  const [selectedClass, setSelectedClass] = useState<ExamClass | null>(null)
  const [selectedSubclass, setSelectedSubclass] = useState<string | null>(null)
  const [sortKey, setSortKey] = useState<SortKey>("name")
  const [page, setPage] = useState(1)

  const allYears = useMemo(() => {
    const set = new Set<number>()
    for (const b of bundles) {
      for (const y of b.years) set.add(y)
    }
    return Array.from(set).sort((a, b) => b - a)
  }, [bundles])

  const baseFiltered = useMemo(() => {
    let result = bundles
    if (debouncedQuery.trim()) {
      const q = debouncedQuery.trim().toLowerCase()
      result = result.filter((b) => b.name.toLowerCase().includes(q))
    }
    if (selectedYear !== null) {
      result = result.filter((b) => b.years.includes(selectedYear))
    }
    return result
  }, [bundles, debouncedQuery, selectedYear])

  const classCounts = useMemo(() => {
    const counts: Record<string, number> = {}
    for (const b of baseFiltered) {
      counts[b.examClass] = (counts[b.examClass] ?? 0) + 1
    }
    return counts
  }, [baseFiltered])

  const availableClasses = useMemo(
    () => EXAM_CLASSES.filter((c) => (classCounts[c] ?? 0) > 0),
    [classCounts]
  )

  const subclassCounts = useMemo(() => {
    const counts: Record<string, number> = {}
    for (const b of baseFiltered) {
      if (selectedClass && b.examClass !== selectedClass) continue
      counts[b.examSubclass] = (counts[b.examSubclass] ?? 0) + 1
    }
    return counts
  }, [baseFiltered, selectedClass])

  const availableSubclasses = useMemo(
    () => Object.keys(subclassCounts).filter((s) => subclassCounts[s] > 0),
    [subclassCounts]
  )

  const filtered = useMemo(() => {
    let result = baseFiltered

    if (selectedClass) {
      result = result.filter((b) => b.examClass === selectedClass)
    }

    if (selectedSubclass) {
      result = result.filter((b) => b.examSubclass === selectedSubclass)
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
  }, [baseFiltered, selectedClass, selectedSubclass, sortKey])

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

  const yearRange = useMemo(() => formatYearRange(allYears), [allYears])

  function handleQueryChange(value: string) {
    setQuery(value)
    setPage(1)
  }

  function handleYearChange(year: number | null) {
    setSelectedYear(year)
    setPage(1)
  }

  function handleClassChange(cls: ExamClass | null) {
    setSelectedClass(cls)
    setSelectedSubclass(null)
    setPage(1)
  }

  function handleSubclassChange(sub: string | null) {
    setSelectedSubclass(sub)
    setPage(1)
  }

  function handleSortChange(key: SortKey) {
    setSortKey(key)
    setPage(1)
  }

  function handleReset() {
    setQuery("")
    setSelectedYear(null)
    setSelectedClass(null)
    setSelectedSubclass(null)
    setPage(1)
  }

  if (error) {
    return (
      <div className="flex min-h-[100dvh] flex-col">
        <PaperGrain />
        <Header totalBundles={0} />
        <div className="flex flex-1 items-center justify-center px-6">
          <div className="flex flex-col items-center text-center">
            <Stamp>載入失敗</Stamp>
            <p className="mt-7 font-medium text-ink-950">資料載入失敗</p>
            <p className="mt-1.5 text-sm text-ink-500">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-5 h-10 rounded-sm border border-line-strong px-4 text-sm font-medium text-ink-800 transition-colors hover:bg-cream"
            >
              重新載入
            </button>
          </div>
        </div>
        <Footer />
      </div>
    )
  }

  return (
    <div className="flex min-h-[100dvh] flex-col">
      <PaperGrain />
      <Header totalBundles={bundles.length} />

      <main className="mx-auto w-full max-w-4xl flex-1 px-6 pb-10 pt-10">
        <section className="flex items-start justify-between gap-8">
          <div>
            <h2 className="font-serif text-3xl font-black tracking-tight text-ink-950 md:text-[2.5rem] md:leading-[1.15]">
              歷屆試題下載
            </h2>
            <p className="mt-3 max-w-[58ch] text-[15px] leading-relaxed text-ink-600">
              收錄國家考試、國營事業甄試、國中會考及技能檢定歷年試題，依類科彙整為多年度
              ZIP 檔，可直接下載。
            </p>
          </div>
          <span
            aria-hidden="true"
            className="hidden shrink-0 select-none border-l border-line pl-4 pt-1 font-serif text-sm tracking-[0.3em] text-ink-400 [writing-mode:vertical-rl] md:block"
          >
            歷屆試題檔案庫
          </span>
        </section>

        {!loading && (
          <div className="mt-8">
            <StatsBar
              total={bundles.length}
              totalFiles={totalFiles}
              yearRange={yearRange}
            />
          </div>
        )}

        {!loading && (
          <div className="mt-6">
            <CategoryFilter
              availableClasses={availableClasses}
              availableSubclasses={availableSubclasses}
              selectedClass={selectedClass}
              selectedSubclass={selectedSubclass}
              onClassChange={handleClassChange}
              onSubclassChange={handleSubclassChange}
              classCounts={classCounts}
              subclassCounts={subclassCounts}
            />
          </div>
        )}

        <div className="mt-6 flex flex-col gap-4">
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

        <div className="mt-8">
          {loading ? (
            <LoadingSkeleton />
          ) : filtered.length === 0 ? (
            <EmptyState onReset={handleReset} />
          ) : (
            <div className="animate-fade-in">
              <p
                className="mb-2 font-mono text-xs text-ink-500"
                aria-live="polite"
              >
                第 {(safePage - 1) * PAGE_SIZE + 1}–
                {Math.min(safePage * PAGE_SIZE, filtered.length)} 筆 · 共{" "}
                {filtered.length.toLocaleString()} 筆
              </p>
              <ul
                role="list"
                className="-mx-4 divide-y divide-line border-y border-line"
              >
                {paginated.map((bundle: Bundle) => (
                  <BundleRow key={bundle.id} bundle={bundle} />
                ))}
              </ul>
              <Pagination
                current={safePage}
                total={totalPages}
                onChange={setPage}
              />
            </div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  )
}

export default App
