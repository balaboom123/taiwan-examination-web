export const EXAM_CLASSES = [
  "公職考試",
  "專技人員考試",
  "國營/就業甄試",
  "教師考試",
  "升學測驗",
  "證照/檢定",
] as const
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
  { idPrefix: "ceec-ast", examClass: "升學測驗", defaultSubclass: "分科測驗" },
  { idPrefix: "ceec-", examClass: "升學測驗", defaultSubclass: "學測" },
  {
    idPrefix: "tcte-tve",
    examClass: "升學測驗",
    defaultSubclass: "四技二專統一入學測驗",
  },
  {
    idPrefix: "special-admission",
    examClass: "升學測驗",
    defaultSubclass: "身心障礙升學甄試",
  },
  { idPrefix: "hce-cmu", examClass: "升學測驗", defaultSubclass: "學士後醫學/中醫" },
  { idPrefix: "hce-tcu", examClass: "升學測驗", defaultSubclass: "學士後醫學/中醫" },
  { idPrefix: "hce-nsysu", examClass: "升學測驗", defaultSubclass: "學士後醫學/中醫" },
  { idPrefix: "hce-nthu", examClass: "升學測驗", defaultSubclass: "學士後醫學/中醫" },
  { idPrefix: "rcpet-cap", examClass: "升學測驗", defaultSubclass: "國中教育會考" },
  { idPrefix: "moea-recruit", examClass: "國營/就業甄試", defaultSubclass: "國營事業聯招" },
  { idPrefix: "post-recruit", examClass: "國營/就業甄試", defaultSubclass: "郵政招考" },
  { idPrefix: "taipower-recruit", examClass: "國營/就業甄試", defaultSubclass: "台電僱員" },
  { idPrefix: "cpc-recruit", examClass: "國營/就業甄試", defaultSubclass: "中油甄試" },
  { idPrefix: "twc-recruit", examClass: "國營/就業甄試", defaultSubclass: "台水甄試" },
  { idPrefix: "taisugar-recruit", examClass: "國營/就業甄試", defaultSubclass: "台糖甄試" },
  { idPrefix: "wdasec-skill", examClass: "證照/檢定", defaultSubclass: "技術士技能檢定" },
  { idPrefix: "teacher-qual", examClass: "教師考試", defaultSubclass: "教師資格檢定" },
  { idPrefix: "teacher-recruit", examClass: "教師考試", defaultSubclass: "教師甄試" },
  { idPrefix: "gept-cert", examClass: "證照/檢定", defaultSubclass: "語言檢定" },
  { idPrefix: "jlpt-cert", examClass: "證照/檢定", defaultSubclass: "語言檢定" },
  { idPrefix: "tocfl-cert", examClass: "證照/檢定", defaultSubclass: "語言檢定" },
  { idPrefix: "hakka-cert", examClass: "證照/檢定", defaultSubclass: "語言檢定" },
  { idPrefix: "taigi-cert", examClass: "證照/檢定", defaultSubclass: "語言檢定" },
  { idPrefix: "tqc-cert", examClass: "證照/檢定", defaultSubclass: "電腦/資訊證照" },
  { idPrefix: "ipas-cert", examClass: "證照/檢定", defaultSubclass: "電腦/資訊證照" },
  { idPrefix: "sfi-", examClass: "證照/檢定", defaultSubclass: "金融證照" },
  { idPrefix: "tabf-", examClass: "證照/檢定", defaultSubclass: "金融證照" },
  { idPrefix: "tii-", examClass: "證照/檢定", defaultSubclass: "金融證照" },
]

const DEFAULT_CLASS: ExamClass = "公職考試"

// --- Per-class classification config ---

interface ClassConfig {
  subclasses: readonly string[]
  rules: readonly [RegExp, string][]
  fallback: string
}

const CLASS_CONFIG: Record<ExamClass, ClassConfig> = {
  公職考試: {
    subclasses: [
      "行政/民政",
      "司法/法律/矯正",
      "財稅/會審/經建",
      "工程/技術",
      "資訊",
      "醫藥衛生",
      "警消/海巡",
      "外交/國際",
      "交通/海事",
      "農林漁牧/環境",
      "教育/文化/新聞",
      "其他公職",
    ],
    rules: [
      [/外交|國際經濟商務|國際新聞|國際[組貿經]/, "外交/國際"],
      [/警察|消防|海巡|海岸巡防|海洋巡護|保安|犯罪防治|鑑識人員|刑事|公共安全人員|調查工作組|化學鑑識/, "警消/海巡"],
      [/醫師|護理|護士|藥師|藥劑|藥事|營養師|物理治療|職能治療|呼吸治療|助產|牙[醫體]|驗光|聽力師|語言治療|臨床心理|諮商心理|公共衛生師|醫[事學用務]|衛生[技檢行]|生藥|中醫師|食品(?!管理)|醫療|心理[測輔]|義肢/, "醫藥衛生"],
      [/律師|法官|司法[官事行]|書記官|公設辯護人|法警|法制|法律[實廉政]|檢察|觀護人|行政執行官|監[獄所]|矯正|公證人|軍法|國防法務|執[行達]員|家事調查官|法院通譯/, "司法/法律/矯正"],
      [/會計[審]?(?!.*工程)|審計|財[務稅產經]|金融|統計|經濟[分行]|記帳|績效審計|關[稅務]|報關|消費者保護/, "財稅/會審/經建"],
      [/資訊[處工管技科組]?$|資訊[處工管技科組]|電腦打字/, "資訊"],
      [/船[長副]|大副|管輪|輪機[長工技]|報務[員]?|航[海空]|飛航|運[輸務]|交通[工技]|船舶[電駕]|漁[船航]|適航|值機員|無線電子員|港[灣務]|海[運事]保險|線務|電信$|機務$/, "交通/海事"],
      [/農[業藝村產]|林業|漁[業撈]|水產|畜牧|獸醫|園藝|自然保育|水[利土]保持|植物|動物技術|養殖|海洋資源|土壤肥料|生物[多技檢資]|環境行政|環保行政/, "農林漁牧/環境"],
      [/教育行政|文化行政|體育行政|博物[管館]|圖書|新聞[行廣編]?|文教|影視|攝影|美工|視聽|宗教|史料/, "教育/文化/新聞"],
      [/工程|測量[技製]?|冶金|結構|建築[工師]|採礦|紡織|冷凍|光電|核[子能]|輻射|機[械檢電]|電[子力機信]工程|化[學工](?!.*鑑識)|環[境保][工技檢]|水利工程|大地|造船|工[礦業]|材料[工程]|都市計畫|景觀|物理$|原子能|同位素|礦冶|職業安全|製造主任|電子[科組]|一般[化工檢]|商品檢驗/, "工程/技術"],
      [/行政|民政|戶政|地政|管理|政風|廉政|僑務|客家|人事|勞工|經建|公[平產]|稅務|安全保防|情報|移民|商業|原住民|法務類|社會|行政[管組警]?|事務|物料|業務[管類]|錄事|庭務|場站|道班|養路|車輛|技術[工類]|營[業繕]|天文|氣象|地[質震]|運務|正[司駕]|副[司駕]|公話|話務|材料管理|印刷|企業|保[育險]人員|家政|餐旅|普通行政|國家安全|土地登記|數理組|政經組|技藝|檢驗員/, "行政/民政"],
    ],
    fallback: "其他公職",
  },
  專技人員考試: {
    subclasses: [
      "法律/會計/專利",
      "商務/保險",
      "醫事/健康",
      "工程技師/建築",
      "不動產/地政",
      "觀光/導遊領隊",
      "海事/航海",
      "農林/獸醫/食品",
      "其他專技",
    ],
    rules: [
      [/不動產|地政士/, "不動產/地政"],
      [/導遊人員|領隊人員/, "觀光/導遊領隊"],
      [/船長|大副|管輪|輪機長|引水人|驗船師|航海/, "海事/航海"],
      [/獸醫師|食品技師|水產養殖技師|畜牧技師|林業技師|農藝技師|園藝技師/, "農林/獸醫/食品"],
      [/保險[經代公證]/, "商務/保險"],
      [/律師$|會計師$|專利師|民間公證人/, "法律/會計/專利"],
      [/醫師|牙醫師|中醫師|法醫師|護理師|護士|藥師|藥劑生|營養師|物理治療師|職能治療師|呼吸治療師|助產士|醫事|驗光|聽力師|語言治療師|心理師|公共衛生師|義肢|社會工作師/, "醫事/健康"],
      [/建築師|技師/, "工程技師/建築"],
    ],
    fallback: "其他專技",
  },
  "國營/就業甄試": {
    subclasses: ["國營事業聯招", "郵政招考", "台電僱員", "中油甄試", "台水甄試", "台糖甄試"],
    rules: [],
    fallback: "國營事業聯招",
  },
  教師考試: {
    subclasses: ["教師資格檢定", "教師甄試"],
    rules: [],
    fallback: "教師資格檢定",
  },
  升學測驗: {
    subclasses: ["學測", "分科測驗", "四技二專統一入學測驗", "身心障礙升學甄試", "學士後醫學/中醫", "國中教育會考"],
    rules: [],
    fallback: "學測",
  },
  "證照/檢定": {
    subclasses: ["技術士技能檢定", "金融證照", "語言檢定", "電腦/資訊證照"],
    rules: [],
    fallback: "技術士技能檢定",
  },
}

// --- Derived exports for UI consumers ---

export const SUBCLASS_ORDER: Record<ExamClass, readonly string[]> =
  Object.fromEntries(
    EXAM_CLASSES.map((c) => [c, CLASS_CONFIG[c].subclasses]),
  ) as Record<ExamClass, readonly string[]>

// --- Classification engine ---

const PUBLIC_SERVICE_NAME_PATTERN = /公職|司法官/

const PROFESSIONAL_NAME_PATTERN =
  /專技|律師$|會計師$|專利師|保險[經代公證]|不動產|地政士|導遊人員|領隊人員|船長|大副|管輪|輪機長|引水人|驗船師|航海|獸醫師|食品技師|水產養殖技師|畜牧技師|林業技師|農藝技師|園藝技師|醫師|牙醫師|中醫師|法醫師|護理師|護士|藥師|藥劑生|營養師|物理治療師|職能治療師|呼吸治療師|助產士|醫事|驗光|聽力師|語言治療師|心理師|公共衛生師|義肢|社會工作師|建築師|技師/

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

function defaultClassForName(name: string): ExamClass {
  if (PUBLIC_SERVICE_NAME_PATTERN.test(name)) return DEFAULT_CLASS
  if (PROFESSIONAL_NAME_PATTERN.test(name)) return "專技人員考試"
  return DEFAULT_CLASS
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
  return classifyByRules(defaultClassForName(name), name)
}
