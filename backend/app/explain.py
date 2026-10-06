"""Explanations: English straight from the DB; Hindi/Marathi rephrased by the LLM once, then cached."""
from sqlmodel import Session

from app.llm.gemini import ExplainResult, GeminiClient
from app.llm.prompts import PROMPT_VERSION
from app.schemas import Explanation
from app.store import ExplanationCache

NO_SOURCE_TEXT = {
    "en": "There is not enough reliable information about this ingredient. Please ask your pharmacist or doctor.",
    "hi": "इस घटक के बारे में पर्याप्त भरोसेमंद जानकारी उपलब्ध नहीं है। कृपया अपने फार्मासिस्ट या डॉक्टर से पूछें।",
    "mr": "या घटकाबद्दल पुरेशी विश्वसनीय माहिती उपलब्ध नाही. कृपया तुमच्या फार्मासिस्ट किंवा डॉक्टरांना विचारा.",
}


def sources_of(drug: dict) -> list[str]:
    return [s for s in [drug["source"], *drug["extra_sources"]] if s]


def from_db(drug: dict) -> ExplainResult:
    return ExplainResult(used_for=drug["used_for"], how_it_works=drug["how_it_works"] or "",
                         how_to_take=drug["how_to_take"], avoid=drug["avoid"],
                         side_effects=drug["common_side_effects"], see_doctor_if=drug["serious_warnings"])


def explain(drug: dict, lang: str, session: Session, llm: GeminiClient) -> Explanation:
    base = {"drug_key": drug["key"], "name": drug["name"], "lang": lang, "sources": sources_of(drug)}
    if drug["no_trusted_source"]:
        return Explanation(**base, available=False, message=NO_SOURCE_TEXT[lang], generated_by="none")
    if lang == "en":
        return Explanation(**base, **from_db(drug).model_dump(), generated_by="database")

    cached = session.get(ExplanationCache, (drug["key"], lang, PROMPT_VERSION))
    if cached:
        body = ExplainResult.model_validate_json(cached.body)
    else:
        body = llm.explain(drug, lang)  # raises LLMError if Gemini fails; nothing is cached then
        session.add(ExplanationCache(drug_key=drug["key"], lang=lang, prompt_version=PROMPT_VERSION,
                                     body=body.model_dump_json()))
        session.commit()
    return Explanation(**base, **body.model_dump(), generated_by="llm")
