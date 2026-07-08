import { StrictMode, type ComponentType } from "react"
import { createRoot } from "react-dom/client"
import "./index.css"
import { AboutPage } from "./pages/about"
import { ContactPage } from "./pages/contact"
import { FaqPage } from "./pages/faq"
import { JoinPage } from "./pages/join"
import { PrivacyPage } from "./pages/privacy"

const PAGES: Record<string, ComponentType> = {
  about: AboutPage,
  contact: ContactPage,
  faq: FaqPage,
  join: JoinPage,
  privacy: PrivacyPage,
}

// GitHub Pages serves both /about.html and the extensionless /about.
const match = /(about|contact|faq|join|privacy)(\.html)?$/.exec(
  window.location.pathname
)
const Page = PAGES[match?.[1] ?? "about"]

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <Page />
  </StrictMode>
)
