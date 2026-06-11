import { Download } from "lucide-react"
import { formatYearRange } from "@/lib/utils"
import type { Bundle } from "@/types"

const MAX_YEAR_CHIPS = 14

export function BundleRow({ bundle }: { bundle: Bundle }) {
  return (
    <li className="flex items-center gap-4 px-4 py-4 transition-colors hover:bg-cream">
      <div className="min-w-0 flex-1">
        <h3 className="font-serif text-[17px] font-semibold leading-snug text-ink-950">
          {bundle.name}
        </h3>
        <p className="mt-1.5 font-mono text-xs text-ink-500">
          民國 {formatYearRange(bundle.years)} · {bundle.fileCount} 份試題
        </p>
        {bundle.years.length > 2 && (
          <p className="mt-1 hidden flex-wrap gap-x-2 font-mono text-[11px] leading-relaxed text-ink-400 sm:flex">
            {bundle.years.slice(0, MAX_YEAR_CHIPS).map((y) => (
              <span key={y}>{y}</span>
            ))}
            {bundle.years.length > MAX_YEAR_CHIPS && (
              <span>+{bundle.years.length - MAX_YEAR_CHIPS}</span>
            )}
          </p>
        )}
      </div>
      <a
        href={bundle.url}
        target="_blank"
        rel="noopener noreferrer"
        aria-label={`下載 ${bundle.name} 試題 ZIP`}
        className="flex h-11 w-11 shrink-0 items-center justify-center gap-2 rounded-[3px] bg-seal-600 text-cream transition-all hover:bg-seal-700 active:translate-y-px sm:w-auto sm:px-4"
      >
        <Download className="size-4" strokeWidth={2} />
        <span className="hidden font-mono text-xs font-medium tracking-[0.15em] sm:inline">
          ZIP
        </span>
      </a>
    </li>
  )
}
