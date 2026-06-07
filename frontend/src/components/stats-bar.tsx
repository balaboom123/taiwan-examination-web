import { Database, Files, CalendarRange } from "lucide-react"

interface StatsBarProps {
  total: number
  totalFiles: number
  yearRange: string
}

export function StatsBar({ total, totalFiles, yearRange }: StatsBarProps) {
  return (
    <div className="flex flex-wrap items-center gap-6 text-sm text-stone-500">
      <span className="flex items-center gap-1.5">
        <Database className="size-4" strokeWidth={1.6} />
        <span className="font-mono">{total.toLocaleString()}</span> 類科
      </span>
      <span className="flex items-center gap-1.5">
        <Files className="size-4" strokeWidth={1.6} />
        <span className="font-mono">{totalFiles.toLocaleString()}</span> 份檔案
      </span>
      <span className="flex items-center gap-1.5">
        <CalendarRange className="size-4" strokeWidth={1.6} />
        {yearRange}
      </span>
    </div>
  )
}
