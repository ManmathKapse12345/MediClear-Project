import { useState } from 'react'
import type { FormEvent } from 'react'
import { api } from '../api'
import EmergencyBanner from '../components/EmergencyBanner.tsx'
import ExplanationView from '../components/ExplanationView.tsx'
import { getStrings } from '../i18n'
import type { AskResponse, Drug, Lang } from '../types'

type Props = {
  lang: Lang
  drug: Drug | null // the medicine last opened with "Explain", if any
}

export default function AskScreen({ lang, drug }: Props) {
  const s = getStrings(lang)
  const [question, setQuestion] = useState('')
  const [aboutDrug, setAboutDrug] = useState(drug !== null) // ticked by default when there is one
  const [loading, setLoading] = useState(false)
  const [answer, setAnswer] = useState<AskResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function handleAsk(e: FormEvent) {
    e.preventDefault()
    const q = question.trim()
    if (!q) return
    setLoading(true)
    setError(null)
    setAnswer(null)
    try {
      setAnswer(await api.ask(q, lang, aboutDrug && drug ? drug.key : undefined))
    } catch (err) {
      setError(err instanceof Error ? err.message : s.status.error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section>
      <h2>{s.askTitle}</h2>

      <form className="search" onSubmit={handleAsk}>
        <label htmlFor="question">{s.questionLabel}</label>
        <textarea
          id="question"
          rows={3}
          maxLength={500}
          value={question}
          placeholder={s.questionPlaceholder}
          onChange={(e) => setQuestion(e.target.value)}
        />

        {drug && (
          <label className="checkbox">
            <input
              type="checkbox"
              checked={aboutDrug}
              onChange={(e) => setAboutDrug(e.target.checked)}
            />
            <span>
              {s.askAbout} <strong>{drug.name}</strong>
            </span>
          </label>
        )}

        <button type="submit" className="primary" disabled={loading || !question.trim()}>
          {s.askButton}
        </button>
      </form>

      {loading && <p role="status">{s.loading}</p>}
      {error && (
        <p className="message error" role="alert">
          {error}
        </p>
      )}
      {answer && <Answer answer={answer} lang={lang} />}
    </section>
  )
}

// Picks how to show the answer from its safety label
function Answer({ answer, lang }: { answer: AskResponse; lang: Lang }) {
  if (answer.label === 'emergency_112') {
    return <EmergencyBanner message={answer.message ?? ''} lang={lang} />
  }
  if (answer.label === 'answer_from_db' && answer.explanation) {
    return (
      <div className="answer">
        <ExplanationView expl={answer.explanation} lang={lang} />
      </div>
    )
  }
  // refuse_to_doctor, not_in_db, stay_in_scope: the backend's fixed, safe text
  return (
    <p className="message" role="alert">
      {answer.message}
    </p>
  )
}