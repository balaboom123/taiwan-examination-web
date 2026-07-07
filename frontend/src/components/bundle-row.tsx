import { type MouseEvent, useEffect, useState } from "react"
import { Download } from "lucide-react"
import { formatYearRange } from "@/lib/utils"
import {
  grantSocialAccess,
  hasSocialAccess,
  socialChannelForBundle,
} from "@/lib/social-gate"
import type { Bundle } from "@/types"

const MAX_YEAR_CHIPS = 14
const SOURCE_NOTES: Record<string, string> = {
  "teacher-qual": "來源：教育部教師資格考試歷屆試題，全國資格考試。",
  "teacher-recruit-newtaipei": "來源：新北市教育人員聯合甄選公告 API，目前收錄 115 學年度。",
  "teacher-recruit-taoyuan-elementary": "來源：桃園市國小教師甄選網，目前收錄 115 學年度。",
  "teacher-recruit-kaohsiung": "來源：高雄市國小與特教教師甄選官方網站，目前收錄 115 學年度。",
  "teacher-recruit-central-alliance": "來源：中區策略聯盟試題疑義網站，官方縣市甄選系統指向此站，目前收錄 115 學年度。",
  "teacher-recruit-tainan": "來源：臺南市國小教師甄選網，目前僅 115 學年度公開 ZIP。",
  "teacher-recruit-taipei-junior": "來源：臺北市教育局公告，目前僅 113–114 學年度國中聯甄。",
}

export function BundleRow({ bundle }: { bundle: Bundle }) {
  const sourceNote = SOURCE_NOTES[bundle.id]
  const socialChannel = socialChannelForBundle(bundle)
  const [canDownload, setCanDownload] = useState(() =>
    hasSocialAccess(socialChannel.id),
  )

  useEffect(() => {
    setCanDownload(hasSocialAccess(socialChannel.id))
  }, [socialChannel.id])

  const href = canDownload ? bundle.url : socialChannel.url
  const actionLabel = canDownload
    ? `下載 ${bundle.name} 試題 ZIP`
    : `前往 ${socialChannel.label}，回來後下載 ${bundle.name} 試題 ZIP`

  function handleClick(event: MouseEvent<HTMLAnchorElement>) {
    if (canDownload) return
    if (hasSocialAccess(socialChannel.id)) {
      event.preventDefault()
      setCanDownload(true)
      window.open(bundle.url, "_blank", "noopener,noreferrer")
      return
    }
    grantSocialAccess(socialChannel.id)
    setCanDownload(true)
  }

  return (
    <li className="flex items-center gap-4 px-4 py-4 transition-colors hover:bg-cream">
      <div className="min-w-0 flex-1">
        <h3 className="font-serif text-[17px] font-semibold leading-snug text-ink-950">
          {bundle.name}
        </h3>
        <p className="mt-1.5 font-mono text-xs text-ink-500">
          民國 {formatYearRange(bundle.years)} · {bundle.fileCount} 份試題
        </p>
        {sourceNote && (
          <p className="mt-1.5 text-xs leading-relaxed text-ink-500">
            {sourceNote}
          </p>
        )}
        <p className="mt-1.5 text-xs leading-relaxed text-ink-500">
          {canDownload ? "社群連結已開啟，可下載 ZIP。" : `先加入「${socialChannel.shortLabel}」後下載。`}
        </p>
        {bundle.years.length > 2 && (
          <p className="mt-1 hidden flex-wrap gap-x-2 font-mono text-[11px] leading-relaxed text-ink-400 sm:flex">
            {bundle.years.slice(0, MAX_YEAR_CHIPS).map((y) => (
              <span key={y}>{y}</span>
            ))}
            {bundle.years.length > MAX_YEAR_CHIPS && (
              <span>+{bundle.years.length - MAX_YEAR_CHIPS}</span>
            )}
          </p>
        )}
      </div>
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        aria-label={actionLabel}
        onClick={handleClick}
        className="flex h-11 w-11 shrink-0 items-center justify-center gap-2 rounded-[3px] bg-seal-600 text-cream transition-all hover:bg-seal-700 active:translate-y-px sm:w-auto sm:px-4"
      >
        <Download className="size-4" strokeWidth={2} />
        <span className="hidden font-mono text-xs font-medium tracking-[0.15em] sm:inline">
          {canDownload ? "ZIP" : "加入"}
        </span>
      </a>
    </li>
  )
}
