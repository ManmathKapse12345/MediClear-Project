import { useState } from "react";
import { LANGS, getStrings } from "./i18n";
import ScanScreen from "./screens/ScanScreen.tsx";
import "./App.css";
import type { Lang } from "./types";
import ExplainScreen from "./screens/ExplainScreen.tsx";

type Tab = "scan" | "explain" | "ask" | "mine";

const LANG_KEY = "mediclear-lang";

function loadLang(): Lang {
  const saved = localStorage.getItem(LANG_KEY);
  return saved === "hi" || saved === "mr" ? saved : "en";
}

function App() {
  const [lang, setLang] = useState<Lang>(loadLang);
  const [tab, setTab] = useState<Tab>("scan");
  const [drugKey, setDrugKey] = useState<string | null>(null); // medicine chosen for "About it"
  const s = getStrings(lang);

  function changeLang(next: Lang) {
    setLang(next);
    localStorage.setItem(LANG_KEY, next);
  }

  function openExplain(key: string) {
    setDrugKey(key);
    setTab("explain");
  }

  const tabs: { id: Tab; label: string }[] = [
    { id: "scan", label: s.tabScan },
    { id: "explain", label: s.tabExplain },
    { id: "ask", label: s.tabAsk },
    { id: "mine", label: s.tabMine },
  ];

  return (
    <div className="app" lang={lang}>
      <header className="topbar">
        <h1>MediClear</h1>
        <div className="lang-picker" role="group" aria-label={s.language}>
          {LANGS.map((l) => (
            <button
              key={l.code}
              className={l.code === lang ? "active" : ""}
              aria-pressed={l.code === lang}
              onClick={() => changeLang(l.code)}
            >
              {l.label}
            </button>
          ))}
        </div>
      </header>

      <nav className="tabs">
        {tabs.map((t) => (
          <button
            key={t.id}
            aria-current={tab === t.id ? "page" : undefined}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </nav>

      <main className="content">
        {tab === "scan" && <ScanScreen lang={lang} onExplain={openExplain} />}
        {tab === "explain" && (
          <ExplainScreen
            key={`${drugKey}-${lang}`}
            lang={lang}
            drugKey={drugKey}
            onFindMedicine={() => setTab("scan")}
          />
        )}
        {tab === "ask" && <p>{s.comingSoon}</p>}
        {tab === "mine" && <p>{s.comingSoon}</p>}
      </main>

      <footer className="disclaimer">{s.disclaimer}</footer>
    </div>
  );
}

export default App;
