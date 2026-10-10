import { useEffect, useState } from 'react'
import { api } from '../api'
import AlertList from '../components/AlertList.tsx'
import { getStrings } from '../i18n'
import type { Lang, MedicineListResponse } from '../types'

// Dates in the user's language, e.g. "9 October 2026" / "९ ऑक्टोबर २०२६"
const LOCALES: Record<Lang, string> = { en: 'en-IN', hi: 'hi-IN', mr: 'mr-IN' }

type Props = {
  lang: Lang
  onFindMedicine: () => void
}

export default function MyMedicinesScreen({ lang, onFindMedicine }: Props) {
  const s = getStrings(lang)
  const [data, setData] = useState<MedicineListResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [attempt, setAttempt] = useState(0) // bump to reload the list
  const [confirmId, setConfirmId] = useState<number | null>(null) // which "Remove" was tapped
  const [busyId, setBusyId] = useState<number | null>(null) // which delete is in progress

  useEffect(() => {
    let ignore = false
    api
      .listMedicines()
      .then((d) => {
        if (!ignore) setData(d)
      })
      .catch((err: Error) => {
        if (!ignore) setError(err.message)
      })
    return () => {
      ignore = true
    }
  }, [attempt])

  function reload() {
    setError(null)
    setAttempt((a) => a + 1)
  }

  async function handleRemove(id: number) {
    setBusyId(id)
    try {
      await api.deleteMedicine(id)
      setConfirmId(null)
      reload() // fetch again: the alerts must be recalculated by the backend
    } catch (err) {
      setError(err instanceof Error ? err.message : s.status.error)
    } finally {
      setBusyId(null)
    }
  }

  if (error) {
    return (
      <div className="message error" role="alert">
        <p>{error}</p>
        <div className="actions">
          <button onClick={reload}>{s.tryAgain}</button>
        </div>
      </div>
    )
  }

  if (!data) return <p role="status">{s.loading}</p>

  if (data.medicines.length === 0) {
    return (
      <div>
        <h2>{s.mineTitle}</h2>
        <p>{s.mineEmpty}</p>
        <button className="primary" onClick={onFindMedicine}>
          {s.tabScan}
        </button>
      </div>
    )
  }

  return (
    <section>
      <h2>{s.mineTitle}</h2>

      {/* Alerts first: they are the most important thing on this screen */}
      {data.alerts.length > 0 ? (
        <>
          <h3 className="alerts-title">{s.alertsTitle}</h3>
          <AlertList alerts={data.alerts} lang={lang} />
        </>
      ) : (
        data.medicines.length > 1 && <p className="message ok">✅ {s.noAlerts}</p>
      )}

      <ul className="med-list">
        {data.medicines.map((med) => (
          <li key={med.id} className="card">
            <h3>{med.label}</h3>
            <p className="note">{med.ingredients.join(', ')}</p>
            <p className="note">
              {s.savedOn}{' '}
              {new Date(med.created_at).toLocaleDateString(LOCALES[lang], {
                day: 'numeric',
                month: 'long',
                year: 'numeric',
              })}
            </p>

            {confirmId === med.id ? (
              <div className="actions">
                <button
                  className="danger"
                  disabled={busyId === med.id}
                  onClick={() => handleRemove(med.id)}
                >
                  {s.confirmRemove}
                </button>
                <button onClick={() => setConfirmId(null)}>{s.cancel}</button>
              </div>
            ) : (
              <button onClick={() => setConfirmId(med.id)}>{s.remove}</button>
            )}
          </li>
        ))}
      </ul>
    </section>
  )
}