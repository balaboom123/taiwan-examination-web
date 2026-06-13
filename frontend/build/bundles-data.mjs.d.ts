export interface ResolvePagesBaseOptions {
  githubRepository?: string
  explicitBase?: string
}

export interface FrontendBundle {
  id: string
  name: string
  years: number[]
  fileCount: number
  url: string
}

export function resolvePagesBase(options?: ResolvePagesBaseOptions): string
export function toFrontendBundles(bundles: unknown): FrontendBundle[]
export function readFrontendBundlesSource(sourcePath: string): Promise<string>
