import type { Plugin } from "vite"
import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"
import tailwindcss from "@tailwindcss/vite"
import path from "path"
// @ts-expect-error Vite can load the ESM build helper directly; runtime behavior is covered by tests.
import { readFrontendBundlesSource, resolveAdsenseEnabled, resolvePagesBase } from "./build/bundles-data.mjs"

const repoRoot = path.resolve(__dirname, "..")
const generatedBundlesPaths = [path.resolve(repoRoot, "data", "sites", "default", "bundles.json")]
const adsensePublisherId = "ca-pub-9524747112096155"
const adsenseAuthorizedSeller = "google.com, pub-9524747112096155, DIRECT, f08c47fec0942fa0"

function servedBundlesPlugin(): Plugin {
  return {
    name: "served-bundles",
    buildStart() {
      for (const generatedBundlesPath of generatedBundlesPaths) {
        this.addWatchFile(generatedBundlesPath)
      }
    },
    configureServer(server) {
      const servedPath = `${server.config.base}data/bundles.json`.replace(/\/{2,}/g, "/")
      const watchedPaths = new Set(generatedBundlesPaths)
      const reloadServedBundles = (file: string) => {
        if (watchedPaths.has(path.resolve(file))) {
          server.ws.send({ type: "full-reload" })
        }
      }

      for (const generatedBundlesPath of generatedBundlesPaths) {
        server.watcher.add(generatedBundlesPath)
      }
      server.watcher.on("add", reloadServedBundles)
      server.watcher.on("change", reloadServedBundles)
      server.watcher.on("unlink", reloadServedBundles)

      server.middlewares.use(async (req, res, next) => {
        const requestPath = req.url?.split("?")[0] ?? ""
        if (requestPath !== servedPath) {
          next()
          return
        }

        try {
          const source = await readFrontendBundlesSource(generatedBundlesPaths)
          res.setHeader("Content-Type", "application/json; charset=utf-8")
          res.end(source)
        } catch (error) {
          res.statusCode = 500
          res.setHeader("Content-Type", "application/json; charset=utf-8")
          res.end(JSON.stringify({ error: error instanceof Error ? error.message : "Failed to load bundle data" }))
        }
      })
    },
    async generateBundle() {
      this.emitFile({
        type: "asset",
        fileName: "data/bundles.json",
        source: await readFrontendBundlesSource(generatedBundlesPaths),
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
    build: {
      rollupOptions: {
        input: {
          main: path.resolve(__dirname, "index.html"),
          about: path.resolve(__dirname, "about.html"),
          contact: path.resolve(__dirname, "contact.html"),
          faq: path.resolve(__dirname, "faq.html"),
          join: path.resolve(__dirname, "join.html"),
          privacy: path.resolve(__dirname, "privacy.html"),
        },
      },
    },
    plugins: [
      servedBundlesPlugin(),
      adsenseAssetsPlugin({ enabled: adsenseEnabled }),
      react(),
      tailwindcss(),
    ],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
  }
})
