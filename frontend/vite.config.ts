import type { Plugin } from "vite"
import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"
import tailwindcss from "@tailwindcss/vite"
import path from "path"
// @ts-expect-error Vite can load the ESM build helper directly; runtime behavior is covered by tests.
import { readFrontendBundlesSource, resolveAdsenseEnabled, resolvePagesBase } from "./build/bundles-data.mjs"

const repoRoot = path.resolve(__dirname, "..")
const generatedBundlesPath = path.resolve(repoRoot, "data", "bundles.json")
const adsensePublisherId = "ca-pub-9524747112096155"
const adsenseAuthorizedSeller = "google.com, pub-9524747112096155, DIRECT, f08c47fec0942fa0"

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

function adsenseAssetsPlugin({ enabled }: { enabled: boolean }): Plugin {
  return {
    name: "adsense-assets",
    transformIndexHtml(html) {
      if (!enabled) {
        return undefined
      }

      return {
        html,
        tags: [
          {
            tag: "meta",
            attrs: {
              name: "google-adsense-account",
              content: adsensePublisherId,
            },
            injectTo: "head",
          },
          {
            tag: "script",
            attrs: {
              async: true,
              src: `https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=${adsensePublisherId}`,
              crossorigin: "anonymous",
            },
            injectTo: "head",
          },
        ],
      }
    },
    generateBundle() {
      if (!enabled) {
        return
      }

      this.emitFile({
        type: "asset",
        fileName: "ads.txt",
        source: `${adsenseAuthorizedSeller}\n`,
      })
    },
  }
}

export default defineConfig(({ command }) => {
  const explicitBase = process.env.VITE_BASE_PATH
  const base = resolvePagesBase({
    githubRepository: process.env.GITHUB_REPOSITORY,
    explicitBase,
  })
  const adsenseEnabled = resolveAdsenseEnabled({
    githubRepository: process.env.GITHUB_REPOSITORY,
    explicitBase,
    explicitEnabled: process.env.VITE_ENABLE_ADSENSE,
    isBuild: command === "build",
  })

  return {
    base,
    plugins: [servedBundlesPlugin(), adsenseAssetsPlugin({ enabled: adsenseEnabled }), react(), tailwindcss()],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
  }
})
