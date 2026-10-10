import { getStrings } from '../i18n'
import type { Lang } from '../types'

type Props = {
  message: string
  lang: Lang
}

export default function EmergencyBanner({ message, lang }: Props) {
  const s = getStrings(lang)
  return (
    <div className="emergency" role="alert">
      <p>⚠️ {message}</p>
      <a className="call-button" href="tel:112">
        {s.call112}
      </a>
    </div>
  )
}