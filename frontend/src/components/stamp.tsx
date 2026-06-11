/** Seal-style stamp mark used for empty and error states. Decorative only. */
export function Stamp({ children }: { children: string }) {
  return (
    <span
      aria-hidden="true"
      className="inline-block -rotate-[5deg] select-none rounded-[4px] border-[3px] border-seal-600/60 px-4 py-1.5 font-serif text-xl font-bold tracking-[0.25em] text-seal-600/70"
    >
      {children}
    </span>
  )
}
