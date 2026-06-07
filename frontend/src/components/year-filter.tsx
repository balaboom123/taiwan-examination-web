import { cn, rocToAd } from "@/lib/utils"

interface YearFilterProps {
  years: number[]
  selected: number | null
  onSelect: (year: number | null) => void
}

export function YearFilter({ years, selected, onSelect }: YearFilterProps) {
  return (
    <div className="relative">
    <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-hide mask-fade-x">
      <button
        onClick={() => onSelect(null)}
        className={cn(
          "shrink-0 h-8 px-3.5 rounded-lg text-sm font-medium transition-all",
          selected === null
            ? "bg-teal-600 text-white"
            : "bg-stone-100 text-stone-500 hover:bg-stone-200 hover:text-stone-700"
        )}
      >
        全部年度
      </button>
      {years.map((year) => (
        <button
          key={year}
          onClick={() => onSelect(year === selected ? null : year)}
          className={cn(
            "shrink-0 h-8 px-3 rounded-lg text-sm font-mono transition-all",
            year === selected
              ? "bg-teal-600 text-white"
              : "bg-stone-100 text-stone-500 hover:bg-stone-200 hover:text-stone-700"
          )}
        >
          {year}
          <span className="text-[10px] ml-0.5 opacity-60">
            ({rocToAd(year)})
          </span>
        </button>
      ))}
    </div>
    </div>
  )
}
