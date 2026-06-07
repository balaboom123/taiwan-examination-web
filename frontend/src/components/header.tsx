import { FileText } from "lucide-react"

export function Header({ totalBundles }: { totalBundles: number }) {
  return (
    <header className="border-b border-stone-200 bg-white/80 backdrop-blur-sm sticky top-0 z-10">
      <div className="max-w-6xl mx-auto flex items-center gap-3 px-6 py-4">
        <div className="flex items-center gap-2.5">
          <div className="size-9 rounded-lg bg-teal-600 flex items-center justify-center">
            <FileText className="size-5 text-white" strokeWidth={1.8} />
          </div>
          <div>
            <h1 className="text-base font-semibold font-[Outfit] tracking-tight text-stone-900 leading-tight">
              考選部歷屆試題
            </h1>
            <p className="text-xs text-stone-800/50 leading-tight">
              MOEX Past Exam Papers
            </p>
          </div>
        </div>
        {totalBundles > 0 && (
          <span className="ml-auto text-xs font-mono text-stone-800/40">
            {totalBundles.toLocaleString()} 類科
          </span>
        )}
      </div>
    </header>
  )
}
