import { ChevronLeft, ChevronRight } from "lucide-react"
import { cn } from "@/lib/utils"

interface PaginationProps {
  current: number
  total: number
  onChange: (page: number) => void
}

export function Pagination({ current, total, onChange }: PaginationProps) {
  if (total <= 1) return null

  const pages: (number | "...")[] = []
  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i)
  } else {
    pages.push(1)
    if (current > 3) pages.push("...")
    for (
      let i = Math.max(2, current - 1);
      i <= Math.min(total - 1, current + 1);
      i++
    ) {
      pages.push(i)
    }
    if (current < total - 2) pages.push("...")
    pages.push(total)
  }

  return (
    <nav className="flex items-center justify-center gap-1 pt-8 pb-4" aria-label="分頁">
      <button
        onClick={() => onChange(current - 1)}
        disabled={current === 1}
        className="size-9 rounded-lg flex items-center justify-center text-stone-500 hover:bg-stone-100 disabled:opacity-30 disabled:pointer-events-none transition-colors"
        aria-label="上一頁"
      >
        <ChevronLeft className="size-4" strokeWidth={2} />
      </button>
      {pages.map((p, i) =>
        p === "..." ? (
          <span key={`dots-${i}`} className="size-9 flex items-center justify-center text-stone-400 text-sm">
            ...
          </span>
        ) : (
          <button
            key={p}
            onClick={() => onChange(p)}
            className={cn(
              "size-9 rounded-lg text-sm font-mono transition-all",
              p === current
                ? "bg-teal-600 text-white"
                : "text-stone-600 hover:bg-stone-100"
            )}
          >
            {p}
          </button>
        )
      )}
      <button
        onClick={() => onChange(current + 1)}
        disabled={current === total}
        className="size-9 rounded-lg flex items-center justify-center text-stone-500 hover:bg-stone-100 disabled:opacity-30 disabled:pointer-events-none transition-colors"
        aria-label="下一頁"
      >
        <ChevronRight className="size-4" strokeWidth={2} />
      </button>
    </nav>
  )
}
