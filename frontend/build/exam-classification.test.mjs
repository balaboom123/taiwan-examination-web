import assert from "node:assert/strict"
import { readFile } from "node:fs/promises"
import test from "node:test"

import ts from "typescript"

async function loadClassifier() {
  const source = await readFile(new URL("../src/lib/exam-classification.ts", import.meta.url), "utf8")
  const { outputText } = ts.transpileModule(source, {
    compilerOptions: {
      module: ts.ModuleKind.ES2022,
      target: ts.ScriptTarget.ES2022,
    },
  })
  const nodeSafeOutput = outputText.replaceAll("import.meta.env.DEV", "false")
  return import(`data:text/javascript;base64,${Buffer.from(nodeSafeOutput).toString("base64")}`)
}

test("teacher bundles are grouped under teacher qualification class", async () => {
  const { classifyBundle } = await loadClassifier()

  assert.deepEqual(classifyBundle("teacher-qual", "教師資格考試"), {
    examClass: "教師資格考試",
    examSubclass: "教師資格考試",
  })
  assert.deepEqual(classifyBundle("teacher-recruit-tainan", "臺南市國小教師甄試"), {
    examClass: "教師資格考試",
    examSubclass: "臺南市國小教師甄試",
  })
  assert.deepEqual(classifyBundle("teacher-recruit-taipei-junior", "臺北市國中教師甄試"), {
    examClass: "教師資格考試",
    examSubclass: "臺北市國中教師甄試",
  })
  assert.deepEqual(classifyBundle("teacher-recruit-newtaipei", "新北市教師甄試"), {
    examClass: "教師資格考試",
    examSubclass: "新北市教師甄試",
  })
  assert.deepEqual(classifyBundle("teacher-recruit-taoyuan-elementary", "桃園市國小教師甄試"), {
    examClass: "教師資格考試",
    examSubclass: "桃園市國小教師甄試",
  })
  assert.deepEqual(classifyBundle("teacher-recruit-kaohsiung", "高雄市教師甄試"), {
    examClass: "教師資格考試",
    examSubclass: "高雄市教師甄試",
  })
  assert.deepEqual(classifyBundle("teacher-recruit-central-alliance", "中區策略聯盟教師甄試"), {
    examClass: "教師資格考試",
    examSubclass: "中區策略聯盟教師甄試",
  })
})

test("language certification bundles are grouped under language proficiency class", async () => {
  const { EXAM_CLASSES, SUBCLASS_ORDER, classifyBundle } = await loadClassifier()

  assert.ok(EXAM_CLASSES.includes("語言檢定"))
  assert.deepEqual(SUBCLASS_ORDER["語言檢定"], [
    "全民英檢 GEPT",
    "TOCFL 華語文能力測驗",
    "客語能力認證",
    "臺灣台語語言能力認證",
  ])
  assert.deepEqual(classifyBundle("gept-cert", "GEPT全民英檢官方練習資料"), {
    examClass: "語言檢定",
    examSubclass: "全民英檢 GEPT",
  })
  assert.deepEqual(classifyBundle("tocfl-cert", "TOCFL華語文能力測驗官方參考資料"), {
    examClass: "語言檢定",
    examSubclass: "TOCFL 華語文能力測驗",
  })
  assert.deepEqual(classifyBundle("hakka-cert", "客語能力認證官方教材及試題"), {
    examClass: "語言檢定",
    examSubclass: "客語能力認證",
  })
  assert.deepEqual(classifyBundle("taigi-cert", "臺灣台語語言能力認證官方試題範例"), {
    examClass: "語言檢定",
    examSubclass: "臺灣台語語言能力認證",
  })
})
