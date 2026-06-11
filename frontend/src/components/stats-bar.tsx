interface StatsBarProps {
  total: number
  totalFiles: number
  yearRange: string
}

export function StatsBar({ total, totalFiles, yearRange }: StatsBarProps) {
  return (
    <dl className="flex flex-wrap items-baseline gap-x-8 gap-y-1.5 border-y border-line py-3 font-mono text-xs text-ink-600">
      <div className="flex items-baseline gap-1.5">
        <dt>收錄類科</dt>
        <dd className="font-medium text-ink-950">{total.toLocaleString()}</dd>
      </div>
      <div className="flex items-baseline gap-1.5">
        <dt>試題檔案</dt>
        <dd className="font-medium text-ink-950">
          {totalFiles.toLocaleString()}
        </dd>
      </div>
      <div className="flex items-baseline gap-1.5">
        <dt>民國年度</dt>
        <dd className="font-medium text-ink-950">{yearRange}</dd>
      </div>
    </dl>
  )
}
