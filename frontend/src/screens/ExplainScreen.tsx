import { useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { api, ApiError } from '../api'
import { getStrings } from '../i18n'
import type { Explanation, Lang } from '../types'

type Props = {
  lang: Lang
  drugKey: string | null
  onFindMedicine: () => void
}

export default function ExplainScreen({ lang, drugKey, onFindMedicine }: Props) {
  const s = getStrings(lang)
  const [readLang, setReadLang] = useState<Lang>(lang) // can switch to 'en' if translation is busy
  const [attempt, setAttempt] = useState(0) // bumping this re-runs the fetch
  const [expl, setExpl] = useState<Explanation | null>(null)
  const [error, setError] = useState<Error | null>(null)
  const [audioFailed, setAudioFailed] = useState(false)

  useEffect(() => {
    if (!drugKey) return
    let ignore = false // set when this request is outdated
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
    setAudioFailed(false)
    setReadLang(nextLang)
    setAttempt((a) => a + 1)
  }

  // 1. Nothing chosen yet (user opened this tab directly)
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

  // 2. The request failed
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

  // 3. Still loading
  if (!expl) return <p role="status">{s.loading}</p>

  // 4. No trusted source: show only the backend's fixed message
  if (!expl.available) {
    return (
      <div>
        <h2>{expl.name}</h2>
        <p className="message">{expl.message}</p>
      </div>
    )
  }

  // 5. The full explanation
  return (
    <article lang={readLang}>
      <h2>{expl.name}</h2>

      <div className="listen">
        <p>
          <strong>{s.listen}</strong>
        </p>
        <audio
          controls
          preload="none"
          src={api.audioUrl(expl.drug_key, readLang)}
          onError={() => setAudioFailed(true)}
        />
        {audioFailed && <p className="note">{s.audioFailed}</p>}
      </div>

      {expl.generated_by === 'llm' && <p className="note">{s.translatedNote}</p>}

      {expl.used_for && (
        <Section title={s.usedFor}>
          <p>{expl.used_for}</p>
        </Section>
      )}
      {expl.how_to_take && (
        <Section title={s.howToTake}>
          <p>{expl.how_to_take}</p>
        </Section>
      )}
      {expl.see_doctor_if.length > 0 && (
        <Section title={s.seeDoctorIf} warn>
          <Points items={expl.see_doctor_if} />
        </Section>
      )}
      {expl.avoid.length > 0 && (
        <Section title={s.avoid}>
          <Points items={expl.avoid} />
        </Section>
      )}
      {expl.side_effects.length > 0 && (
        <Section title={s.sideEffects}>
          <Points items={expl.side_effects} />
        </Section>
      )}
      {expl.how_it_works && (
        <Section title={s.howItWorks}>
          <p>{expl.how_it_works}</p>
        </Section>
      )}

      {expl.sources.length > 0 && (
        <div className="note sources">
          <p>{s.sources}:</p>
          <ul>
            {expl.sources.map((src) => (
              <li key={src}>
                {src.startsWith('http') ? (
                  <a href={src} target="_blank" rel="noreferrer">
                    {src}
                  </a>
                ) : (
                  src
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </article>
  )
}

// One big card with a heading
function Section({ title, warn, children }: { title: string; warn?: boolean; children: ReactNode }) {
  return (
    <section className={warn ? 'card warn' : 'card'}>
      <h3>{title}</h3>
      {children}
    </section>
  )
}

// A bulleted list of short points
function Points({ items }: { items: string[] }) {
  return (
    <ul className="points">
      {items.map((item, i) => (
        <li key={i}>{item}</li>
      ))}
    </ul>
  )
}