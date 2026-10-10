import { useState } from 'react'
import type { ReactNode } from 'react'
import { api } from '../api'
import { getStrings } from '../i18n'
import type { Explanation, Lang } from '../types'

type Props = {
  expl: Explanation
  lang: Lang // the app's language, used for the headings
}

export default function ExplanationView({ expl, lang }: Props) {
  const s = getStrings(lang)
  const [audioFailed, setAudioFailed] = useState(false)

  // No trusted source: show only the backend's fixed message
  if (!expl.available) {
    return (
      <div>
        <h2>{expl.name}</h2>
        <p className="message">{expl.message}</p>
      </div>
    )
  }

  return (
    <article lang={expl.lang}>
      <h2>{expl.name}</h2>

      <div className="listen">
        <p>
          <strong>{s.listen}</strong>
        </p>
        <audio
          controls
          preload="none"
          src={api.audioUrl(expl.drug_key, expl.lang)}
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

function Section({ title, warn, children }: { title: string; warn?: boolean; children: ReactNode }) {
  return (
    <section className={warn ? 'card warn' : 'card'}>
      <h3>{title}</h3>
      {children}
    </section>
  )
}

function Points({ items }: { items: string[] }) {
  return (
    <ul className="points">
      {items.map((item, i) => (
        <li key={i}>{item}</li>
      ))}
    </ul>
  )
}