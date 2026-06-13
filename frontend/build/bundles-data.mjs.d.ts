export interface ResolvePagesBaseOptions {
  githubRepository?: string
  explicitBase?: string
}

export interface ResolveAdsenseEnabledOptions extends ResolvePagesBaseOptions {
  explicitEnabled?: string | boolean
  isBuild?: boolean
}

export interface FrontendBundle {
  id: string
  name: string
  years: number[]
  fileCount: number
  url: string
}

export function resolvePagesBase(options?: ResolvePagesBaseOptions): string
export function resolveAdsenseEnabled(options?: ResolveAdsenseEnabledOptions): boolean
export function toFrontendBundles(bundles: unknown): FrontendBundle[]
export function readFrontendBundlesSource(sourcePath: string): Promise<string>
