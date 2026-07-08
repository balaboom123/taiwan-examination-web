import { InfoLayout } from "./info-layout"
import { siteHref } from "@/lib/utils"

export function FaqPage() {
  return (
    <InfoLayout
      title="常見問題"
      lead="下載方式、資料範圍與回報管道的快速說明。"
      ornament="常見問題"
      active="faq"
    >
      <h2>如何下載試題？</h2>
      <p>
        在首頁搜尋考試類科（例如「護理師」、「律師」），或用分類與年度篩選，找到後點選右側紅色下載鈕，即可取得該類科的多年度
        ZIP 檔。
      </p>

      <h2>為什麼下載前要先加入 LINE 社群？</h2>
      <p>
        本站免費維運，LINE
        社群是我們維持更新動力、也讓考生互相交流的方式。第一次下載時會先開啟社群邀請連結，之後同一瀏覽器即自動解鎖，可直接下載所有檔案。
      </p>

      <h2>年度是民國還是西元？</h2>
      <p>
        以民國（ROC）年度為主，並在括號附上西元年份對照，例如「民國
        104–114（2015–2025）」。
      </p>

      <h2>下載的檔案是什麼格式？</h2>
      <p>
        每個類科為一個 ZIP 壓縮檔，內含歷年試題
        PDF；是否附答案依各命題機關公開的內容而定。
      </p>

      <h2>找不到我的類科，或缺少某個年度？</h2>
      <p>
        可能是官方尚未公開，或本站尚未收錄。歡迎透過
        <a href={siteHref("contact.html")}>GitHub Issue 或電子郵件</a>
        回報，我們會盡快補上。
      </p>

      <h2>試題內容有問題怎麼辦？</h2>
      <p>
        所有檔案皆為官方公開內容的鏡像，未經修改。若發現封存錯誤（檔案損毀、年度標示錯誤等），請
        <a href={siteHref("contact.html")}>與我們聯絡</a>。
      </p>

      <h2>本站是官方網站嗎？</h2>
      <p>
        不是。本站為非官方彙整，與考選部及各命題機關無任何隸屬關係，詳見
        <a href={siteHref("privacy.html")}>隱私權與免責聲明</a>。
      </p>
    </InfoLayout>
  )
}
