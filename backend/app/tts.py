"""Text-to-speech for explanations. Only DB-backed text is ever spoken; each MP3 is made once and cached."""
import hashlib
from io import BytesIO

from gtts import gTTS, gTTSError
from sqlmodel import Session

from app.schemas import Explanation
from app.store import AudioCache

HEADINGS = {  # (avoid, side effects, see a doctor)
    "en": ("Avoid", "Common side effects", "See a doctor if you have"),
    "hi": ("इनसे बचें", "आम साइड इफ़ेक्ट", "इनमें से कुछ हो तो डॉक्टर से मिलें"),
    "mr": ("हे टाळा", "सामान्य दुष्परिणाम", "यापैकी काही झाल्यास डॉक्टरांना भेटा"),
}


class TTSError(Exception):
    """gTTS failed (no network, rate limit, Google changed something)."""


def speech_text(expl: Explanation) -> str:
    if not expl.available:
        return f"{expl.name}. {expl.message}"
    avoid, side, doctor = HEADINGS[expl.lang]
    parts = [expl.name, expl.used_for, expl.how_to_take]
    for heading, items in ((avoid, expl.avoid), (side, expl.side_effects), (doctor, expl.see_doctor_if)):
        if items:
            parts.append(f"{heading}: {', '.join(items)}")
    # a full stop between parts gives a pause; strip existing ones so we don't get ".."
    return ". ".join(p.strip().rstrip(".।") for p in parts if p.strip())


def synthesize(text: str, lang: str) -> bytes:
    buf = BytesIO()
    try:
        gTTS(text, lang=lang).write_to_fp(buf)  # gTTS supports en, hi and mr
    except gTTSError as e:
        raise TTSError(str(e)) from e
    return buf.getvalue()


def cached_mp3(text: str, lang: str, session: Session) -> bytes:
    key = hashlib.sha256(f"{lang}\n{text}".encode()).hexdigest()
    if cached := session.get(AudioCache, key):
        return cached.mp3
    mp3 = synthesize(text, lang)  # raises TTSError; nothing is cached then
    session.add(AudioCache(text_hash=key, mp3=mp3))
    session.commit()
    return mp3
