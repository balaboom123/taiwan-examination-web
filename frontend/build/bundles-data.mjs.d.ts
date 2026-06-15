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

export interface LootLabsManifestEntry {
  canonical_id: string
  asset_name: string
  loot_url: string
  target_download_url: string
  target_checksum: string
  updated_at: string
}

export interface LootLabsManifest {
  version: number
  provider: "lootlabs"
  settings: {
    tier_id: number
    number_of_tasks: number
    theme: number
  }
  bundles: Record<string, LootLabsManifestEntry>
}

export function resolvePagesBase(options?: ResolvePagesBaseOptions): string
export function resolveAdsenseEnabled(options?: ResolveAdsenseEnabledOptions): boolean
export function toFrontendBundles(
  bundles: unknown,
  options?: { lootlabsManifest?: LootLabsManifest },
): FrontendBundle[]
export function readFrontendBundlesSource(
  sourcePath: string,
  options?: { lootlabsManifestPath?: string },
): Promise<string>
