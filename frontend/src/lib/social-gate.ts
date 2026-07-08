const ACCESS_KEY = "taiwan-exam-download-access"
// Older builds granted access per channel; those keys still count as unlocked.
const LEGACY_ACCESS_KEYS = ["public-service", "cap", "gsat-ast"].map(
  (id) => `${ACCESS_KEY}:${id}`,
)

export interface SocialChannel {
  id: string
  shortLabel: string
  label: string
  url: string
}

/** All community channels; every join button opens the same channel list. */
export const SOCIAL_CHANNELS: readonly SocialChannel[] = [
  {
    id: "public-service",
    shortLabel: "公職國考討論",
    label: "公職國考討論-最新考試資訊/職缺情報/經驗分享",
    url: "https://line.me/ti/g2/BbtDmyVsB-xV-dRc2WfItQC2xz0ImRxDmQVycg?utm_source=invitation&utm_medium=link_copy&utm_campaign=default",
  },
  {
    id: "cap",
    shortLabel: "會考討論群",
    label: "會考討論群— 找書友一起認真/題目討論/讀書分享",
    url: "https://line.me/ti/g2/MhOvoVeolNCiW378gPYpwxNd_UKOSkeyh-8k0Q?utm_source=invitation&utm_medium=link_copy&utm_campaign=default",
  },
  {
    id: "gsat-ast",
    shortLabel: "學測分科討論群",
    label: "學測分科討論群— 題目討論/用書分享/選系問答",
    url: "https://line.me/ti/g2/MN4eYdpSgoM56-DgqE9k-NtOJKQ_nbnJWeqVSQ?utm_source=invitation&utm_medium=link_copy&utm_campaign=default",
  },
]

export function hasSocialAccess(): boolean {
  try {
    return [ACCESS_KEY, ...LEGACY_ACCESS_KEYS].some(
      (key) => window.localStorage.getItem(key) === "1",
    )
  } catch {
    return false
  }
}

export function grantSocialAccess() {
  try {
    window.localStorage.setItem(ACCESS_KEY, "1")
  } catch {
    // Browser storage can be blocked; component state still unlocks this tab.
  }
}
