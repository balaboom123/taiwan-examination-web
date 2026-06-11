export function LoadingSkeleton() {
  return (
    <div
      aria-hidden="true"
      className="-mx-4 divide-y divide-line border-y border-line"
    >
      {Array.from({ length: 8 }, (_, i) => (
        <div key={i} className="flex items-center gap-4 px-4 py-4">
          <div className="flex-1">
            <div className="skeleton h-5 w-44 max-w-[60%]" />
            <div className="skeleton mt-2 h-3.5 w-64 max-w-[80%]" />
          </div>
          <div className="skeleton h-11 w-11 shrink-0 sm:w-[88px]" />
        </div>
      ))}
    </div>
  )
}
