import { cn } from "@/lib/utils"
import type { ExamClass } from "@/lib/exam-classification"
import { EXAM_CLASSES, SUBCLASS_ORDER } from "@/lib/exam-classification"

interface CategoryFilterProps {
  availableClasses: ExamClass[]
  availableSubclasses: string[]
  selectedClass: ExamClass | null
  selectedSubclass: string | null
  onClassChange: (cls: ExamClass | null) => void
  onSubclassChange: (sub: string | null) => void
  classCounts: Record<string, number>
  subclassCounts: Record<string, number>
}

export function CategoryFilter({
  availableClasses,
  availableSubclasses,
  selectedClass,
  selectedSubclass,
  onClassChange,
  onSubclassChange,
  classCounts,
  subclassCounts,
}: CategoryFilterProps) {
  const orderedClasses = EXAM_CLASSES.filter((c) => availableClasses.includes(c))
  const orderedSubclasses = selectedClass
    ? (SUBCLASS_ORDER[selectedClass] ?? []).filter((s) =>
        availableSubclasses.includes(s)
      )
    : []

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-hide">
        <button
          onClick={() => onClassChange(null)}
          aria-pressed={selectedClass === null}
          className={cn(
            "h-9 shrink-0 rounded-[3px] border px-3.5 text-sm font-medium transition-colors",
            selectedClass === null
              ? "border-ink-950 bg-ink-950 text-cream"
              : "border-line bg-cream text-ink-600 hover:border-line-strong hover:text-ink-950"
          )}
        >
          全部分類
        </button>
        {orderedClasses.map((cls) => (
          <button
            key={cls}
            onClick={() => onClassChange(cls === selectedClass ? null : cls)}
            aria-pressed={cls === selectedClass}
            className={cn(
              "h-9 shrink-0 rounded-[3px] border px-3.5 text-sm font-medium transition-colors",
              cls === selectedClass
                ? "border-ink-950 bg-ink-950 text-cream"
                : "border-line bg-cream text-ink-600 hover:border-line-strong hover:text-ink-950"
            )}
          >
            {cls}
            <span className="ml-1.5 text-[11px] opacity-60">
              {classCounts[cls] ?? 0}
            </span>
          </button>
        ))}
      </div>

      {selectedClass && orderedSubclasses.length > 0 && (
        <div className="mask-fade-x flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-hide">
          <button
            onClick={() => onSubclassChange(null)}
            aria-pressed={selectedSubclass === null}
            className={cn(
              "h-8 shrink-0 rounded-[3px] border px-3 text-xs font-medium transition-colors",
              selectedSubclass === null
                ? "border-seal-600 bg-seal-600 text-cream"
                : "border-line bg-cream text-ink-600 hover:border-line-strong hover:text-ink-950"
            )}
          >
            全部
          </button>
          {orderedSubclasses.map((sub) => (
            <button
              key={sub}
              onClick={() =>
                onSubclassChange(sub === selectedSubclass ? null : sub)
              }
              aria-pressed={sub === selectedSubclass}
              className={cn(
                "h-8 shrink-0 rounded-[3px] border px-3 text-xs font-medium transition-colors",
                sub === selectedSubclass
                  ? "border-seal-600 bg-seal-600 text-cream"
                  : "border-line bg-cream text-ink-600 hover:border-line-strong hover:text-ink-950"
              )}
            >
              {sub}
              <span className="ml-1 text-[10px] opacity-60">
                {subclassCounts[sub] ?? 0}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
