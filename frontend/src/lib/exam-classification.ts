export const EXAM_CLASSES = ["公職", "升學", "國營事業", "技檢", "金融證照"] as const
export type ExamClass = (typeof EXAM_CLASSES)[number]

export interface ExamCategory {
  examClass: ExamClass
  examSubclass: string
}

// --- Provider routing ---
// Each route maps a bundle ID prefix to a class.
// If defaultSubclass is set, the bundle skips pattern matching entirely.
// If not set, the bundle is classified by that class's subclass rules.

interface ProviderRoute {
  idPrefix: string
  examClass: ExamClass
  defaultSubclass?: string
}

const PROVIDER_ROUTES: readonly ProviderRoute[] = [
  { idPrefix: "ceec-", examClass: "升學", defaultSubclass: "學測" },
  { idPrefix: "rcpet-cap", examClass: "升學", defaultSubclass: "國中教育會考" },
  { idPrefix: "moea-recruit", examClass: "國營事業", defaultSubclass: "國營事業聯招" },
  { idPrefix: "taipower-recruit", examClass: "國營事業", defaultSubclass: "台電僱員" },
  { idPrefix: "cpc-recruit", examClass: "國營事業", defaultSubclass: "中油甄試" },
  { idPrefix: "twc-recruit", examClass: "國營事業", defaultSubclass: "台水甄試" },
  { idPrefix: "taisugar-recruit", examClass: "國營事業", defaultSubclass: "台糖甄試" },
  { idPrefix: "wdasec-skill", examClass: "技檢", defaultSubclass: "技術士技能檢定" },
  { idPrefix: "sfi-", examClass: "金融證照" },
  { idPrefix: "tabf-", examClass: "金融證照" },
  { idPrefix: "tii-", examClass: "金融證照" },
]

const DEFAULT_CLASS: ExamClass = "公職"

// --- Per-class classification config ---

interface ClassConfig {
  subclasses: readonly string[]
  rules: readonly [RegExp, string][]
  fallback: string
}

const CLASS_CONFIG: Record<ExamClass, ClassConfig> = {
  公職: {
    subclasses: [
      "行政類科",
      "法律類科",
      "商科類科",
      "技術類科",
      "資訊類科",
      "醫藥衛生",
      "警消海巡",
      "外交國際",
      "交通海事",
      "農林漁牧",
      "文教類科",
      "導遊領隊",
      "其他",
    ],
    rules: [
      [/導遊人員|領隊人員/, "導遊領隊"],
      [/外交|國際經濟商務|國際新聞|國際[組貿經]/, "外交國際"],
      [/警察|消防|海巡|海岸巡防|海洋巡護|保安|犯罪防治|鑑識人員|刑事|公共安全人員|調查工作組|化學鑑識/, "警消海巡"],
      [/醫師|護理|護士|藥師|藥劑|藥事|營養師|物理治療|職能治療|呼吸治療|助產|牙[醫體]|驗光|聽力師|語言治療|臨床心理|諮商心理|公共衛生師|醫[事學用務]|衛生[技檢行]|生藥|中醫師|食品(?!管理)|醫療|心理[測輔]|義肢/, "醫藥衛生"],
      [/律師|法官|司法[官事行]|書記官|公設辯護人|法警|法制|法律[實廉政]|檢察|觀護人|行政執行官|監[獄所]|矯正|公證人|軍法|國防法務|執[行達]員|家事調查官|法院通譯/, "法律類科"],
      [/會計[師審]?(?!.*工程)|審計|財[務稅產經]|金融|保險[人經代公]|統計|經濟[分行]|記帳|績效審計|關[稅務]|不動產[估經]|專[利責]|報關|消費者保護/, "商科類科"],
      [/資訊[處工管技科組]?$|資訊[處工管技科組]|電腦打字/, "資訊類科"],
      [/船[長副]|大副|管輪|輪機[長工技]|報務[員]?|引水人|航[海空]|飛航|運[輸務]|交通[工技]|船舶[電駕]|漁[船航]|適航|值機員|無線電子員|港[灣務]|海[運事]保險|驗船|線務|電信$|機務$/, "交通海事"],
      [/農[業藝村產]|林業|漁[業撈]|水產|畜牧|獸醫|園藝|自然保育|水[利土]保持|植物|動物技術|養殖|海洋資源|土壤肥料|生物[多技檢資]/, "農林漁牧"],
      [/教育行政|文化行政|體育行政|博物[管館]|圖書|新聞[行廣編]?|文教|影視|攝影|美工|視聽|宗教|史料/, "文教類科"],
      [/工程[技師]?|技師|測量[技製]?|冶金|結構|建築[工師]|採礦|紡織|冷凍|光電|核[子能]|輻射|機[械檢電]|電[子力機信]工程|化[學工](?!.*鑑識)|環[境保][工技檢]|水利工程|大地|造船|工[礦業]|材料[工程]|都市計畫|景觀|物理$|原子能|同位素|礦冶|職業安全|製造主任|電子[科組]|一般[化工檢]|商品檢驗/, "技術類科"],
      [/行政|民政|戶政|地政|管理|政風|廉政|僑務|客家|人事|勞工|經建|公[平產]|稅務|安全保防|情報|移民|商業|原住民|法務類|社會|行政[管組警]?|事務|物料|業務[管類]|錄事|庭務|場站|道班|養路|車輛|技術[工類]|營[業繕]|天文|氣象|地[質震]|運務|正[司駕]|副[司駕]|公話|話務|材料管理|印刷|企業|保[育險]人員|家政|餐旅|普通行政|國家安全|土地登記|數理組|政經組|技藝|檢驗員/, "行政類科"],
    ],
    fallback: "其他",
  },
  升學: {
    subclasses: ["學測", "國中教育會考"],
    rules: [],
    fallback: "學測",
  },
  國營事業: {
    subclasses: ["國營事業聯招", "台電僱員", "中油甄試", "台水甄試", "台糖甄試"],
    rules: [],
    fallback: "國營事業聯招",
  },
  技檢: {
    subclasses: ["技術士技能檢定"],
    rules: [],
    fallback: "技術士技能檢定",
  },
  金融證照: {
    subclasses: ["證券期貨", "銀行金融", "保險", "其他"],
    rules: [
      [/證券|期貨|投信投顧|企業內部控制|票券|股務|資產證券化|工商倫理/, "證券期貨"],
      [/銀行|信託|理財規劃|外匯|授信|風險管理|債權催收|數位金融|洗錢|金融科技|資產評估/, "銀行金融"],
      [/保險/, "保險"],
    ],
    fallback: "其他",
  },
}

// --- Derived exports for UI consumers ---

export const SUBCLASS_ORDER: Record<ExamClass, readonly string[]> =
  Object.fromEntries(
    EXAM_CLASSES.map((c) => [c, CLASS_CONFIG[c].subclasses]),
  ) as Record<ExamClass, readonly string[]>

// --- Classification engine ---

function classifyByRules(examClass: ExamClass, name: string): ExamCategory {
  const config = CLASS_CONFIG[examClass]
  for (const [pattern, subclass] of config.rules) {
    if (pattern.test(name)) {
      return { examClass, examSubclass: subclass }
    }
  }
  if (import.meta.env.DEV) {
    console.warn(
      `[exam-classification] fallback hit: "${name}" → ${examClass}/${config.fallback}`,
    )
  }
  return { examClass, examSubclass: config.fallback }
}

export function classifyBundle(id: string, name: string): ExamCategory {
  for (const route of PROVIDER_ROUTES) {
    if (id.startsWith(route.idPrefix)) {
      if (route.defaultSubclass) {
        return {
          examClass: route.examClass,
          examSubclass: route.defaultSubclass,
        }
      }
      return classifyByRules(route.examClass, name)
    }
  }
  return classifyByRules(DEFAULT_CLASS, name)
}
