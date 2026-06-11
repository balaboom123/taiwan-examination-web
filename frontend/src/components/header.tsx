export function Header({ totalBundles }: { totalBundles: number }) {
  return (
    <header className="sticky top-0 z-10 border-t-[3px] border-b border-t-ink-950 border-b-line bg-paper/95 backdrop-blur-sm">
      <div className="mx-auto flex h-16 max-w-4xl items-center gap-3 px-6">
        <span
          aria-hidden="true"
          className="flex size-9 shrink-0 select-none items-center justify-center rounded-[4px] bg-seal-600 font-serif text-lg font-bold text-cream"
        >
          試
        </span>
        <div className="min-w-0">
          <h1 className="font-serif text-[17px] font-bold leading-tight tracking-wide text-ink-950">
            考選部歷屆試題
          </h1>
          <p className="text-[10px] leading-tight tracking-[0.22em] text-ink-500">
            國家考試試題檔案庫
          </p>
        </div>
        {totalBundles > 0 && (
          <span className="ml-auto font-mono text-xs text-ink-500">
            {totalBundles.toLocaleString()} 類科
          </span>
        )}
      </div>
    </header>
  )
}
