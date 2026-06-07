import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function rocToAd(roc: number): number {
  return roc + 1911
}

export function formatYearRange(years: number[]): string {
  if (years.length === 0) return ""
  if (years.length === 1) return `${years[0]} (${rocToAd(years[0])})`
  const newest = years[0]
  const oldest = years[years.length - 1]
  return `${oldest}–${newest} (${rocToAd(oldest)}–${rocToAd(newest)})`
}
