"""Safety router. Keywords catch the dangerous cases first; the LLM only picks a label. Replies are fixed text."""
import re
import unicodedata

from app.llm.gemini import GeminiClient, Label, LLMError

# Safest first. When two checks disagree, the label earlier in this list wins.
SAFETY_ORDER: list[Label] = ["emergency_112", "refuse_to_doctor", "stay_in_scope", "not_in_db", "answer_from_db"]


def norm(text: str) -> str:
    # Hindi/Marathi letters like "ज़" can be typed two ways; NFC makes them compare equal
    return unicodedata.normalize("NFC", text)


def patterns(*words: str) -> list[re.Pattern]:
    return [re.compile(norm(w), re.IGNORECASE) for w in words]


# \b only for English: Python's \b does not work inside Devanagari words, so those are plain substrings.
RED_FLAGS: dict[Label, list[re.Pattern]] = {
    "emergency_112": patterns(
        r"\b(accidental(ly)?|by mistake|overdose|too many)\b", r"\btook \d+",
        r"\bswell", r"can'?t breathe|trouble breathing|short(ness)? of breath", r"chest pain",
        r"\b(unconscious|fainted|passed out|seizure|convulsion)", r"\b(shaking|sweating|confused)\b",
        r"bleeding|vomit\w* blood|blood in",
        # Hindi
        "गलती से", "साँस|सांस", "बेहोश", "खून की उलटी", "सूज",
        # Marathi
        "चुकून", "श्वास", "बेशुद्ध", "उलटीतून रक्त|रक्तस्त्राव|रक्त येत",
    ),
    "refuse_to_doctor": patterns(
        r"\b(stop|quit|skip|missed|forgot|double|switch|change|increase|reduce|extra)\b",
        r"\bat once\b|\bmore than\b|\bfaster\b|\bmore often\b|\btwo (tablets|pills|doses)\b",
        r"pregnan|breast-?feed", r"\b(child|baby|kid|infant|son|daughter)\b|year[- ]old",
        r"\bshould i buy\b|\bwhich one\b",
        # Hindi
        "बंद", "बच्च", "गर्भ", "ज़्यादा|ज्यादा", "दोगुना", "छोड़",
        # Marathi
        "मुल", "बाळ", "गरोदर", "जास्त", "दुप्पट",
    ),
}

MESSAGES: dict[Label, dict[str, str]] = {
    "emergency_112": {
        "en": "This may be an emergency. Call 112 now or go to the nearest hospital. Take the medicine strip or box with you.",
        "hi": "यह आपातकालीन स्थिति हो सकती है। अभी 112 पर कॉल करें या नज़दीकी अस्पताल जाएँ। दवा का पत्ता या डिब्बा साथ ले जाएँ।",
        "mr": "ही आपत्कालीन परिस्थिती असू शकते. आत्ताच 112 वर कॉल करा किंवा जवळच्या रुग्णालयात जा. औषधाची स्ट्रिप किंवा डबा सोबत घ्या.",
    },
    "refuse_to_doctor": {
        "en": "I can't advise on this. Please ask your doctor or pharmacist before you start, stop or change any medicine.",
        "hi": "मैं इस बारे में सलाह नहीं दे सकता। कोई भी दवा शुरू करने, बंद करने या बदलने से पहले अपने डॉक्टर या फार्मासिस्ट से पूछें।",
        "mr": "मी याबद्दल सल्ला देऊ शकत नाही. कोणतेही औषध सुरू करण्यापूर्वी, बंद करण्यापूर्वी किंवा बदलण्यापूर्वी तुमच्या डॉक्टर किंवा फार्मासिस्टना विचारा.",
    },
    "not_in_db": {
        "en": "I don't have verified information about this. Please ask your pharmacist or doctor.",
        "hi": "मेरे पास इसकी भरोसेमंद जानकारी नहीं है। कृपया अपने फार्मासिस्ट या डॉक्टर से पूछें।",
        "mr": "माझ्याकडे याची विश्वसनीय माहिती नाही. कृपया तुमच्या फार्मासिस्ट किंवा डॉक्टरांना विचारा.",
    },
    "stay_in_scope": {
        "en": "I can only explain the medicines in MediClear, using checked information. I can't change these rules.",
        "hi": "मैं केवल MediClear में दी गई दवाओं को जाँची हुई जानकारी से समझा सकता हूँ। मैं ये नियम नहीं बदल सकता।",
        "mr": "मी फक्त MediClear मधील औषधे तपासलेल्या माहितीच्या आधारे समजावू शकतो. मी हे नियम बदलू शकत नाही.",
    },
}


def safer(a: Label, b: Label) -> Label:
    return min(a, b, key=SAFETY_ORDER.index)


def keyword_label(question: str) -> Label | None:
    text = norm(question)
    for label in SAFETY_ORDER:  # emergency is checked before refuse
        if any(p.search(text) for p in RED_FLAGS.get(label, [])):
            return label
    return None


def route(question: str, drug: dict | None, llm: GeminiClient) -> Label:
    kw = keyword_label(question)
    try:
        label = llm.classify_question(question, drug and drug["name"])
    except LLMError:
        label = "refuse_to_doctor"  # fail safe, never fail open
    if kw:
        label = safer(kw, label)
    if label == "answer_from_db" and (drug is None or drug["no_trusted_source"]):
        label = "not_in_db"
    return label
