import { SearchX } from "lucide-react"

export function EmptyState({ onReset }: { onReset: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <div className="size-14 rounded-2xl bg-stone-100 flex items-center justify-center mb-4">
        <SearchX className="size-7 text-stone-400" strokeWidth={1.5} />
      </div>
      <p className="text-base font-medium text-stone-900">
        查無相符類科
      </p>
      <p className="mt-1 text-sm text-stone-500">
        請調整搜尋條件或年度篩選
      </p>
      <button
        onClick={onReset}
        className="mt-4 h-9 px-4 rounded-lg text-sm font-medium bg-stone-100 text-stone-700 hover:bg-stone-200 transition-colors"
      >
        清除條件
      </button>
    </div>
  )
}
