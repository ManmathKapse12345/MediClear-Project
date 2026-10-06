"""Photo -> medicine. Gemini reads the pack; the matcher and the DB decide what it is. In doubt: low_confidence."""
import re
from dataclasses import replace

from app.kb import KnowledgeBase
from app.llm.gemini import GeminiClient, VisionResult
from app.matcher import MatchResult, identify, match_ingredient

MIN_CONFIDENCE = 0.6
NUMBER = re.compile(r"(\d[\d,]*(?:\.\d+)?)\s*(gm|g|mg|mcg|iu|ml)?\b", re.IGNORECASE)


def numbers(text: str | None) -> set[float]:
    """'1 gm' -> {1.0, 1000.0}; '60,000 IU (1500 mcg)' -> {60000.0, 1500.0}"""
    out = set()
    for value, unit in NUMBER.findall(text or ""):
        v = float(value.replace(",", ""))
        out.add(v)
        if unit.lower() in ("g", "gm"):
            out.add(v * 1000)  # grams -> mg, so "1 gm" matches "1000 mg"
    return out


def brand_conflicts(kb: KnowledgeBase, brand: str, vision: VisionResult) -> list[str]:
    """Ways the photo disagrees with the matched brand. Empty list = consistent."""
    strengths = {i["key"]: i["strength"] for i in kb.brands[brand]["ingredients"]}
    reasons = []
    for ing in vision.ingredients:
        key = match_ingredient(kb, ing.name)
        if key is None:
            continue  # a name we don't know can't confirm or contradict the brand
        if key not in strengths:
            reasons.append(f"The pack lists {ing.name}, which {brand} does not contain.")
        elif ing.strength and strengths[key] and not numbers(ing.strength) & numbers(strengths[key]):
            reasons.append(f"The pack says {ing.name} {ing.strength}, but {brand} has {strengths[key]}.")
    return reasons


def confirmed_by_ingredients(kb: KnowledgeBase, brand: str, vision: VisionResult) -> bool:
    keys = {i["key"] for i in kb.brands[brand]["ingredients"]}
    return any(match_ingredient(kb, i.name) in keys for i in vision.ingredients)


def identify_photo(kb: KnowledgeBase, llm: GeminiClient, image: bytes, mime_type: str) -> MatchResult:
    vision = llm.vision_extract(image, mime_type)  # LLMError goes up; the router turns it into status "error"
    if not vision.readable:
        return MatchResult("unreadable")
    result = identify(kb, vision.brand_text, [i.name for i in vision.ingredients])
    if result.status != "ok":
        return result
    if vision.confidence < MIN_CONFIDENCE:
        return replace(result, status="low_confidence", reasons=["The photo is not clear enough."])
    if result.brand:
        reasons = brand_conflicts(kb, result.brand, vision)
        if result.score < 100 and not confirmed_by_ingredients(kb, result.brand, vision):
            reasons.append(f"The name on the pack only partly matches {result.brand}.")
        if reasons:
            return replace(result, status="low_confidence", reasons=reasons)
    return result
