import { Search, X } from "lucide-react"

interface SearchBarProps {
  value: string
  onChange: (value: string) => void
}

export function SearchBar({ value, onChange }: SearchBarProps) {
  return (
    <div className="relative">
      <Search
        className="absolute left-4 top-1/2 -translate-y-1/2 size-5 text-stone-300 pointer-events-none"
        strokeWidth={1.8}
      />
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="搜尋考試類科 ..."
        className="w-full h-12 pl-12 pr-12 text-base bg-white border border-stone-200 rounded-xl text-stone-900 placeholder:text-stone-300 transition-colors focus:border-teal-500 focus:outline-none"
      />
      {value && (
        <button
          onClick={() => onChange("")}
          className="absolute right-3 top-1/2 -translate-y-1/2 size-7 rounded-md flex items-center justify-center text-stone-400 hover:text-stone-600 hover:bg-stone-100 transition-colors"
          aria-label="清除搜尋"
        >
          <X className="size-4" strokeWidth={2} />
        </button>
      )}
    </div>
  )
}
