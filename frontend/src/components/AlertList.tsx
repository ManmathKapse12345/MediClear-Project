import { getStrings } from '../i18n'
import type { AlertLevel, InteractionAlert, Lang } from '../types'

// Every level has its own icon AND word, so colour is never the only signal
const ICONS: Record<AlertLevel, string> = {
  warning: '⛔',
  caution: '⚠️',
  timing: '🕒',
}

type Props = {
  alerts: InteractionAlert[]
  lang: Lang
}

export default function AlertList({ alerts, lang }: Props) {
  const s = getStrings(lang)
  return (
    <ul className="alerts">
      {alerts.map((a, i) => (
        <li key={i} className={`alert alert-${a.level}`}>
          <p className="alert-title">
            <span aria-hidden="true">{ICONS[a.level]}</span> {s.level[a.level]}:{' '}
            {a.between.join(' + ')}
          </p>
          <p>
            <strong>{s.levelAdvice[a.level]}</strong>
          </p>
          {lang !== 'en' && <p className="note">{s.detailsInEnglish}</p>}
          <p lang="en">{a.message}</p>
          {a.sources.length > 0 && (
            <p className="note">
              {s.sources}:
              {a.sources.map((src, j) => (
                <span key={src}>
                  {' '}
                  <a href={src} target="_blank" rel="noreferrer">
                    [{j + 1}]
                  </a>
                </span>
              ))}
            </p>
          )}
        </li>
      ))}
    </ul>
  )
}