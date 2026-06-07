export function LoadingSkeleton() {
  return (
    <div className="flex flex-col gap-3">
      {Array.from({ length: 8 }, (_, i) => (
        <div
          key={i}
          className="bg-white border border-stone-200/80 rounded-xl p-5 animate-fade-up"
          style={{ animationDelay: `${i * 60}ms` }}
        >
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 space-y-3">
              <div className="skeleton h-5 w-48" />
              <div className="flex gap-4">
                <div className="skeleton h-4 w-32" />
                <div className="skeleton h-4 w-20" />
              </div>
            </div>
            <div className="skeleton size-10 rounded-lg shrink-0" />
          </div>
        </div>
      ))}
    </div>
  )
}
