import assert from "node:assert/strict"
import { readFile } from "node:fs/promises"
import test from "node:test"

import ts from "typescript"

async function loadClassifier() {
  return loadTsModule("../src/lib/exam-classification.ts")
}

async function loadTsModule(relativePath) {
  const source = await readFile(new URL(relativePath, import.meta.url), "utf8")
  const { outputText } = ts.transpileModule(source, {
    compilerOptions: {
      module: ts.ModuleKind.ES2022,
      target: ts.ScriptTarget.ES2022,
    },
  })
  const nodeSafeOutput = outputText.replaceAll("import.meta.env.DEV", "false")
  return import(`data:text/javascript;base64,${Buffer.from(nodeSafeOutput).toString("base64")}`)
}

async function loadSocialGate() {
  return loadTsModule("../src/lib/social-gate.ts")
}

test("teacher bundles are grouped under teacher qualification class", async () => {
  const { classifyBundle } = await loadClassifier()

  assert.deepEqual(classifyBundle("teacher-qual", "教師資格考試"), {
    examClass: "教師考試",
    examSubclass: "教師資格檢定",
  })
  assert.deepEqual(classifyBundle("teacher-recruit-tainan", "臺南市國小教師甄試"), {
    examClass: "教師考試",
    examSubclass: "教師甄試",
  })
  assert.deepEqual(classifyBundle("teacher-recruit-taipei-junior", "臺北市國中教師甄試"), {
    examClass: "教師考試",
    examSubclass: "教師甄試",
  })
  assert.deepEqual(classifyBundle("teacher-recruit-newtaipei", "新北市教師甄試"), {
    examClass: "教師考試",
    examSubclass: "教師甄試",
  })
  assert.deepEqual(classifyBundle("teacher-recruit-taoyuan-elementary", "桃園市國小教師甄試"), {
    examClass: "教師考試",
    examSubclass: "教師甄試",
  })
  assert.deepEqual(classifyBundle("teacher-recruit-kaohsiung", "高雄市教師甄試"), {
    examClass: "教師考試",
    examSubclass: "教師甄試",
  })
  assert.deepEqual(classifyBundle("teacher-recruit-central-alliance", "中區策略聯盟教師甄試"), {
    examClass: "教師考試",
    examSubclass: "教師甄試",
  })
})

test("MOEX professional exams are separated from public-service exams", async () => {
  const { EXAM_CLASSES, SUBCLASS_ORDER, classifyBundle } = await loadClassifier()

  assert.ok(EXAM_CLASSES.includes("專技人員考試"))
  assert.deepEqual(SUBCLASS_ORDER["專技人員考試"], [
    "法律/會計/專利",
    "商務/保險",
    "醫事/健康",
    "工程技師/建築",
    "不動產/地政",
    "觀光/導遊領隊",
    "海事/航海",
    "農林/獸醫/食品",
    "其他專技",
  ])
  assert.deepEqual(classifyBundle("canonical-lawyer", "律師"), {
    examClass: "專技人員考試",
    examSubclass: "法律/會計/專利",
  })
  assert.deepEqual(classifyBundle("canonical-accountant", "會計師"), {
    examClass: "專技人員考試",
    examSubclass: "法律/會計/專利",
  })
  assert.deepEqual(classifyBundle("canonical-insurance-agent", "人身保險代理人"), {
    examClass: "專技人員考試",
    examSubclass: "商務/保險",
  })
  assert.deepEqual(classifyBundle("canonical-nurse", "護理師"), {
    examClass: "專技人員考試",
    examSubclass: "醫事/健康",
  })
  assert.deepEqual(classifyBundle("canonical-civil-engineer", "土木工程技師"), {
    examClass: "專技人員考試",
    examSubclass: "工程技師/建築",
  })
  assert.deepEqual(classifyBundle("canonical-realtor", "不動產經紀人"), {
    examClass: "專技人員考試",
    examSubclass: "不動產/地政",
  })
  assert.deepEqual(classifyBundle("canonical-land-agent", "地政士"), {
    examClass: "專技人員考試",
    examSubclass: "不動產/地政",
  })
  assert.deepEqual(classifyBundle("canonical-land-admin", "地政"), {
    examClass: "公職考試",
    examSubclass: "行政/民政",
  })
  assert.deepEqual(classifyBundle("canonical-public-nurse", "公職護理師"), {
    examClass: "公職考試",
    examSubclass: "醫藥衛生",
  })
  assert.deepEqual(classifyBundle("canonical-public-architect", "公職建築師"), {
    examClass: "公職考試",
    examSubclass: "工程/技術",
  })
})

test("language certification bundles are grouped under language proficiency class", async () => {
  const { EXAM_CLASSES, SUBCLASS_ORDER, classifyBundle } = await loadClassifier()

  assert.ok(EXAM_CLASSES.includes("證照/檢定"))
  assert.deepEqual(SUBCLASS_ORDER["證照/檢定"], [
    "技術士技能檢定",
    "金融證照",
    "語言檢定",
    "電腦/資訊證照",
  ])
  assert.deepEqual(classifyBundle("gept-cert", "GEPT全民英檢官方練習資料"), {
    examClass: "證照/檢定",
    examSubclass: "語言檢定",
  })
  assert.deepEqual(classifyBundle("jlpt-cert", "JLPT Japanese-Language Proficiency Test"), {
    examClass: "證照/檢定",
    examSubclass: "語言檢定",
  })
  assert.deepEqual(classifyBundle("tocfl-cert", "TOCFL華語文能力測驗官方參考資料"), {
    examClass: "證照/檢定",
    examSubclass: "語言檢定",
  })
  assert.deepEqual(classifyBundle("hakka-cert", "客語能力認證官方教材及試題"), {
    examClass: "證照/檢定",
    examSubclass: "語言檢定",
  })
  assert.deepEqual(classifyBundle("taigi-cert", "臺灣台語語言能力認證官方試題範例"), {
    examClass: "證照/檢定",
    examSubclass: "語言檢定",
  })
})

test("IT certification bundles are grouped under computer information certification class", async () => {
  const { EXAM_CLASSES, SUBCLASS_ORDER, classifyBundle } = await loadClassifier()

  assert.ok(EXAM_CLASSES.includes("證照/檢定"))
  assert.deepEqual(classifyBundle("tqc-cert", "TQC官方範例試卷"), {
    examClass: "證照/檢定",
    examSubclass: "電腦/資訊證照",
  })
  assert.deepEqual(classifyBundle("ipas-cert-ise", "iPAS 資訊安全工程師"), {
    examClass: "證照/檢定",
    examSubclass: "電腦/資訊證照",
  })
  assert.deepEqual(classifyBundle("ipas-cert-oia", "iPAS 營運智慧分析師"), {
    examClass: "證照/檢定",
    examSubclass: "電腦/資訊證照",
  })
  assert.deepEqual(classifyBundle("ipas-cert-aiap", "iPAS AI應用規劃師"), {
    examClass: "證照/檢定",
    examSubclass: "電腦/資訊證照",
  })
  assert.deepEqual(classifyBundle("ipas-cert-aiot", "iPAS AIoT應用工程師"), {
    examClass: "證照/檢定",
    examSubclass: "電腦/資訊證照",
  })
  assert.deepEqual(classifyBundle("wdasec-skill", "全國技術士技能檢定"), {
    examClass: "證照/檢定",
    examSubclass: "技術士技能檢定",
  })
})

test("download gate access is global and honors legacy per-channel keys", async () => {
  const { grantSocialAccess, hasSocialAccess, SOCIAL_CHANNELS } =
    await loadSocialGate()
  const previousWindow = globalThis.window
  const storage = new Map()

  globalThis.window = {
    localStorage: {
      getItem: (key) => storage.get(key) ?? null,
      setItem: (key, value) => storage.set(key, value),
    },
  }

  try {
    assert.equal(SOCIAL_CHANNELS.length, 3)
    assert.equal(hasSocialAccess(), false)

    grantSocialAccess()
    assert.equal(hasSocialAccess(), true)

    storage.clear()
    storage.set("taiwan-exam-download-access:cap", "1")
    assert.equal(hasSocialAccess(), true)
  } finally {
    if (previousWindow === undefined) {
      delete globalThis.window
    } else {
      globalThis.window = previousWindow
    }
  }
})
