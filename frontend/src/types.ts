export interface BundlePart {
  label: string
  url: string
  fileCount: number
}

export interface Bundle {
  id: string
  name: string
  years: number[]
  fileCount: number
  url: string
  parts?: BundlePart[]
  examClass: string
  examSubclass: string
  domainId?: string
  examFamilyId?: string
  seriesId?: string
  levelId?: string
  trackId?: string
  variantIds?: string[]
  stageId?: string
}
