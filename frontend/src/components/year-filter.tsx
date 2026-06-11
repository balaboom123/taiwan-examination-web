import { cn, rocToAd } from "@/lib/utils"

interface YearFilterProps {
  years: number[]
  selected: number | null
  onSelect: (year: number | null) => void
}

export function YearFilter({ years, selected, onSelect }: YearFilterProps) {
  return (
    <div className="mask-fade-x flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-hide">
      <button
        onClick={() => onSelect(null)}
        aria-pressed={selected === null}
        className={cn(
          "h-9 shrink-0 rounded-[3px] border px-3.5 text-sm font-medium transition-colors",
          selected === null
            ? "border-ink-950 bg-ink-950 text-cream"
            : "border-line bg-cream text-ink-600 hover:border-line-strong hover:text-ink-950"
        )}
      >
        全部年度
      </button>
      {years.map((year) => (
        <button
          key={year}
          onClick={() => onSelect(year === selected ? null : year)}
          aria-pressed={year === selected}
          className={cn(
            "h-9 shrink-0 rounded-[3px] border px-3 font-mono text-sm transition-colors",
            year === selected
              ? "border-ink-950 bg-ink-950 text-cream"
              : "border-line bg-cream text-ink-600 hover:border-line-strong hover:text-ink-950"
          )}
        >
          {year}
          <span className="ml-1 text-[10px] opacity-60">{rocToAd(year)}</span>
        </button>
      ))}
    </div>
  )
}
