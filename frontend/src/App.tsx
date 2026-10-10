import AskScreen from "./screens/AskScreen.tsx";
import type { Drug, Lang } from "./types";
import { useState } from "react";
import { LANGS, getStrings } from "./i18n";
import ScanScreen from "./screens/ScanScreen.tsx";
import "./App.css";
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
  const [drug, setDrug] = useState<Drug | null>(null); // medicine chosen with "Explain"
  const s = getStrings(lang);

  function changeLang(next: Lang) {
    setLang(next);
    localStorage.setItem(LANG_KEY, next);
  }

  function openExplain(key: string, name: string) {
    setDrug({ key, name });
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
            key={`${drug?.key}-${lang}`}
            lang={lang}
            drugKey={drug?.key ?? null}
            onFindMedicine={() => setTab("scan")}
          />
        )}
        {tab === "ask" && <AskScreen lang={lang} drug={drug} />}
        {tab === "mine" && <p>{s.comingSoon}</p>}
      </main>

      <footer className="disclaimer">{s.disclaimer}</footer>
    </div>
  );
}

export default App;
