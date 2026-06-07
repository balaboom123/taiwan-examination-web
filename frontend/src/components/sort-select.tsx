import { ArrowUpDown } from "lucide-react"
import { cn } from "@/lib/utils"

export type SortKey = "name" | "files-desc" | "years-desc"

interface SortSelectProps {
  value: SortKey
  onChange: (value: SortKey) => void
}

const options: { value: SortKey; label: string }[] = [
  { value: "name", label: "名稱" },
  { value: "files-desc", label: "檔案數" },
  { value: "years-desc", label: "年度數" },
]

export function SortSelect({ value, onChange }: SortSelectProps) {
  return (
    <div className="flex items-center gap-1.5">
      <ArrowUpDown className="size-4 text-stone-400" strokeWidth={1.8} />
      <div className="flex items-center gap-0.5 bg-stone-100 rounded-lg p-0.5">
        {options.map((opt) => (
          <button
            key={opt.value}
            onClick={() => onChange(opt.value)}
            className={cn(
              "h-7 px-2.5 rounded-md text-sm transition-all",
              value === opt.value
                ? "bg-white text-stone-900 shadow-sm"
                : "text-stone-500 hover:text-stone-700"
            )}
          >
            {opt.label}
          </button>
        ))}
      </div>
    </div>
  )
}
