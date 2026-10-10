import { useEffect, useState } from 'react'
import { api, ApiError } from '../api'
import ExplanationView from '../components/ExplanationView.tsx'
import { getStrings } from '../i18n'
import type { Explanation, Lang } from '../types'

type Props = {
  lang: Lang
  drugKey: string | null
  onFindMedicine: () => void
}

export default function ExplainScreen({ lang, drugKey, onFindMedicine }: Props) {
  const s = getStrings(lang)
  const [readLang, setReadLang] = useState<Lang>(lang)
  const [attempt, setAttempt] = useState(0)
  const [expl, setExpl] = useState<Explanation | null>(null)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    if (!drugKey) return
    let ignore = false
    api
      .explain(drugKey, readLang)
      .then((data) => {
        if (!ignore) setExpl(data)
      })
      .catch((err: Error) => {
        if (!ignore) setError(err)
      })
    return () => {
      ignore = true
    }
  }, [drugKey, readLang, attempt])

  function retry(nextLang: Lang) {
    setError(null)
    setExpl(null)
    setReadLang(nextLang)
    setAttempt((a) => a + 1)
  }

  if (!drugKey) {
    return (
      <div>
        <p>{s.noMedicine}</p>
        <button className="primary" onClick={onFindMedicine}>
          {s.tabScan}
        </button>
      </div>
    )
  }

  if (error) {
    const busy = error instanceof ApiError && error.status === 503
    return (
      <div className="message error" role="alert">
        <p>{busy ? s.translationBusy : error.message}</p>
        <div className="actions">
          {busy && readLang !== 'en' && (
            <button className="primary" onClick={() => retry('en')}>
              {s.readInEnglish}
            </button>
          )}
          <button onClick={() => retry(readLang)}>{s.tryAgain}</button>
        </div>
      </div>
    )
  }

  if (!expl) return <p role="status">{s.loading}</p>

  return <ExplanationView expl={expl} lang={lang} />
}