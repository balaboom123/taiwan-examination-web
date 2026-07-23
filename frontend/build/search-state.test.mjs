import assert from "node:assert/strict"
import { readFile } from "node:fs/promises"
import test from "node:test"
import ts from "typescript"

async function loadSearchState() {
  const source = await readFile(new URL("../src/lib/search-state.ts", import.meta.url), "utf8")
  const { outputText } = ts.transpileModule(source, {
    compilerOptions: {
      module: ts.ModuleKind.ES2022,
      target: ts.ScriptTarget.ES2022,
    },
  })
  return import(`data:text/javascript;base64,${Buffer.from(outputText).toString("base64")}`)
}

test("search state round-trips filters into a shareable query", async () => {
  const { buildSearchQuery, readSearchState } = await loadSearchState()
  const state = readSearchState("?q=%E8%AD%B7%E7%90%86%E5%B8%AB&year=114&class=%E5%B0%88%E6%8A%80%E4%BA%BA%E5%93%A1%E8%80%83%E8%A9%A6&subclass=%E9%86%AB%E4%BA%8B%2F%E5%81%A5%E5%BA%B7&sort=files-desc&page=3")

  assert.deepEqual(state, {
    query: "護理師",
    year: 114,
    examClass: "專技人員考試",
    subclass: "醫事/健康",
    sort: "files-desc",
    page: 3,
  })
  assert.equal(
    buildSearchQuery(state),
    "q=%E8%AD%B7%E7%90%86%E5%B8%AB&year=114&class=%E5%B0%88%E6%8A%80%E4%BA%BA%E5%93%98%E8%80%83%E8%A9%A6&subclass=%E9%86%AB%E4%BA%8B%2F%E5%81%A5%E5%BA%B7&sort=files-desc&page=3",
  )
})

test("invalid URL values fall back to safe defaults", async () => {
  const { readSearchState } = await loadSearchState()
  assert.deepEqual(readSearchState("?year=nope&page=0&sort=unknown"), {
    query: "",
    year: null,
    examClass: null,
    subclass: null,
    sort: "name",
    page: 1,
  })
})
