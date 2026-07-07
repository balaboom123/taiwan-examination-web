import type { Bundle } from "@/types"

const ACCESS_KEY_PREFIX = "taiwan-exam-download-access:"

export interface SocialChannel {
  id: string
  shortLabel: string
  label: string
  url: string
}

const PUBLIC_SERVICE_CHANNEL: SocialChannel = {
  id: "public-service",
  shortLabel: "公職國考討論",
  label: "公職國考討論-最新考試資訊/職缺情報/經驗分享",
  url: "https://line.me/ti/g2/BbtDmyVsB-xV-dRc2WfItQC2xz0ImRxDmQVycg?utm_source=invitation&utm_medium=link_copy&utm_campaign=default",
}

const CAP_CHANNEL: SocialChannel = {
  id: "cap",
  shortLabel: "會考討論群",
  label: "會考討論群— 找書友一起認真/題目討論/讀書分享",
  url: "https://line.me/ti/g2/MhOvoVeolNCiW378gPYpwxNd_UKOSkeyh-8k0Q?utm_source=invitation&utm_medium=link_copy&utm_campaign=default",
}

const GSAT_AST_CHANNEL: SocialChannel = {
  id: "gsat-ast",
  shortLabel: "學測分科討論群",
  label: "學測分科討論群— 題目討論/用書分享/選系問答",
  url: "https://line.me/ti/g2/MN4eYdpSgoM56-DgqE9k-NtOJKQ_nbnJWeqVSQ?utm_source=invitation&utm_medium=link_copy&utm_campaign=default",
}

export function socialChannelForBundle(
  bundle: Pick<Bundle, "examClass" | "examSubclass">,
): SocialChannel {
  if (bundle.examClass === "升學測驗") {
    if (bundle.examSubclass === "國中教育會考") return CAP_CHANNEL
    if (bundle.examSubclass === "學測" || bundle.examSubclass === "分科測驗") {
      return GSAT_AST_CHANNEL
    }
  }

  return PUBLIC_SERVICE_CHANNEL
}

export function hasSocialAccess(channelId: string): boolean {
  try {
    return window.localStorage.getItem(`${ACCESS_KEY_PREFIX}${channelId}`) === "1"
  } catch {
    return false
  }
}

export function grantSocialAccess(channelId: string) {
  try {
    window.localStorage.setItem(`${ACCESS_KEY_PREFIX}${channelId}`, "1")
  } catch {
    // Browser storage can be blocked; component state still unlocks this tab.
  }
}
