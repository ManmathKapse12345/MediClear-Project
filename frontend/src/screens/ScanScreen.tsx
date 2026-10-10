import { useState } from 'react'
import type { ChangeEvent, FormEvent } from 'react'
import { api } from '../api'
import { getStrings } from '../i18n'
import type { IdentifyResponse, Lang } from '../types'

type Props = {
  lang: Lang
  onExplain: (drugKey: string, name: string) => void
}

export default function ScanScreen({ lang, onExplain }: Props) {
  const s = getStrings(lang)
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<IdentifyResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [saved, setSaved] = useState(false)

  // Shared by text search and photo: reset, call the backend, store the result
  async function identify(call: () => Promise<IdentifyResponse>) {
    setLoading(true)
    setError(null)
    setResult(null)
    setSaved(false)
    try {
      setResult(await call())
    } catch (err) {
      setError(err instanceof Error ? err.message : s.status.error)
    } finally {
      setLoading(false)
    }
  }

  function handleSearch(e: FormEvent) {
    e.preventDefault() // stop the browser from reloading the page
    const q = query.trim()
    if (q) identify(() => api.identifyText(q))
  }

  function handlePhoto(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    e.target.value = '' // so choosing the same photo again still triggers onChange
    if (file) identify(() => api.identifyPhoto(file))
  }

  async function handleSave() {
    if (!result) return
    // Save the whole medicine (brand + all its ingredients), because
    // interaction checks compare medicines, not single ingredients
    const label = result.brand ?? result.ingredients.map((i) => i.name).join(' + ')
    try {
      await api.saveMedicine({ label, ingredients: result.ingredients.map((i) => i.key) })
      setSaved(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : s.status.error)
    }
  }

  return (
    <section>
      <h2>{s.scanTitle}</h2>

      <form className="search" onSubmit={handleSearch}>
        <label htmlFor="query">{s.searchLabel}</label>
        <input
          id="query"
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          maxLength={200}
          autoComplete="off"
        />
        <button type="submit" className="primary" disabled={loading || !query.trim()}>
          {s.searchButton}
        </button>
      </form>

      <p className="or">{s.or}</p>

      <label className="button photo-button">
        {s.photoButton}
        <input
          className="visually-hidden"
          type="file"
          accept="image/*"
          capture="environment"
          onChange={handlePhoto}
          disabled={loading}
        />
      </label>

      {loading && <p role="status">{s.loading}</p>}

      {error && (
        <p className="message error" role="alert">
          {error}
        </p>
      )}

      {result && result.status !== 'ok' && (
        <p className="message" role="alert">
          {s.status[result.status]}
        </p>
      )}

      {result?.status === 'ok' && (
        <div className="card">
          {result.brand && <h3>{result.brand}</h3>}
          <p>{s.contains}</p>
          <ul className="ingredients">
            {result.ingredients.map((ing) => (
              <li key={ing.key}>
                <span>
                  <strong>{ing.name}</strong>
                  {ing.strength && ` ${ing.strength}`}
                </span>
                <button onClick={() => onExplain(ing.key, ing.name)}>{s.explain}</button>
              </li>
            ))}
          </ul>
          {result.unverified.length > 0 && (
            <p className="note">
              {s.unverified} {result.unverified.join(', ')}
            </p>
          )}
          <button className="primary wide" onClick={handleSave} disabled={saved}>
            {saved ? s.saved : s.save}
          </button>
        </div>
      )}
    </section>
  )
}