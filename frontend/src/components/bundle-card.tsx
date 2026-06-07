import { Download, FileArchive, Calendar } from "lucide-react"
import { formatYearRange } from "@/lib/utils"
import type { Bundle } from "@/types"

export function BundleCard({ bundle }: { bundle: Bundle }) {
  return (
    <div className="group bg-white border border-stone-200/80 rounded-xl p-5 transition-all hover:border-stone-300 hover:shadow-[0_4px_24px_-8px_rgba(0,0,0,0.06)]">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <h3 className="text-[15px] font-semibold text-stone-900 leading-snug truncate">
            {bundle.name}
          </h3>
          <div className="mt-2.5 flex flex-wrap items-center gap-x-4 gap-y-1.5 text-sm text-stone-500">
            <span className="flex items-center gap-1.5">
              <Calendar className="size-3.5" strokeWidth={1.8} />
              <span className="font-mono text-xs">
                {formatYearRange(bundle.years)}
              </span>
            </span>
            <span className="flex items-center gap-1.5">
              <FileArchive className="size-3.5" strokeWidth={1.8} />
              <span className="font-mono text-xs">
                {bundle.fileCount} 份
              </span>
            </span>
          </div>
          {bundle.years.length > 2 && (
            <div className="mt-2 flex flex-wrap gap-1">
              {bundle.years.slice(0, 12).map((y) => (
                <span
                  key={y}
                  className="inline-block h-5 px-1.5 rounded bg-amber-100/60 text-[11px] font-mono text-amber-700 leading-5"
                >
                  {y}
                </span>
              ))}
              {bundle.years.length > 12 && (
                <span className="inline-block h-5 px-1.5 rounded bg-stone-100 text-[11px] font-mono text-stone-400 leading-5">
                  +{bundle.years.length - 12}
                </span>
              )}
            </div>
          )}
        </div>
        <a
          href={bundle.url}
          target="_blank"
          rel="noopener noreferrer"
          className="shrink-0 size-10 rounded-lg bg-teal-600 flex items-center justify-center text-white transition-all hover:bg-teal-700 active:scale-95"
          aria-label={`下載 ${bundle.name}`}
          title="下載 ZIP"
        >
          <Download className="size-4.5" strokeWidth={2} />
        </a>
      </div>
    </div>
  )
}
