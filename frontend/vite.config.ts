import type { Plugin } from "vite"
import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"
import tailwindcss from "@tailwindcss/vite"
import path from "path"
// @ts-expect-error Vite can load the ESM build helper directly; runtime behavior is covered by tests.
import { readFrontendBundlesSource, resolvePagesBase } from "./build/bundles-data.mjs"

const repoRoot = path.resolve(__dirname, "..")
const generatedBundlesPath = path.resolve(repoRoot, "data", "bundles.json")

function servedBundlesPlugin(): Plugin {
  return {
    name: "served-bundles",
    buildStart() {
      this.addWatchFile(generatedBundlesPath)
    },
    configureServer(server) {
      const servedPath = `${server.config.base}data/bundles.json`.replace(/\/{2,}/g, "/")
      server.watcher.add(generatedBundlesPath)
      server.watcher.on("change", (file) => {
        if (path.resolve(file) === generatedBundlesPath) {
          server.ws.send({ type: "full-reload" })
        }
      })

      server.middlewares.use(async (req, res, next) => {
        const requestPath = req.url?.split("?")[0] ?? ""
        if (requestPath !== servedPath) {
          next()
          return
        }

        try {
          const source = await readFrontendBundlesSource(generatedBundlesPath)
          res.setHeader("Content-Type", "application/json; charset=utf-8")
          res.end(source)
        } catch (error) {
          res.statusCode = 500
          res.setHeader("Content-Type", "application/json; charset=utf-8")
          res.end(
            JSON.stringify({
              error: error instanceof Error ? error.message : "Failed to load generated bundles data",
            }),
          )
        }
      })
    },
    async generateBundle() {
      this.emitFile({
        type: "asset",
        fileName: "data/bundles.json",
        source: await readFrontendBundlesSource(generatedBundlesPath),
      })
    },
  }
}

export default defineConfig({
  base: resolvePagesBase({
    githubRepository: process.env.GITHUB_REPOSITORY,
    explicitBase: process.env.VITE_BASE_PATH,
  }),
  plugins: [servedBundlesPlugin(), react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
})
