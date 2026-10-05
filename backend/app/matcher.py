"""Turns text read off a pack into database entries. No confident match means no explanation."""
import re
from dataclasses import dataclass, field

from rapidfuzz import fuzz, process

from app.kb import KnowledgeBase, norm

BRAND_THRESHOLD = 85       # fuzzy score (0-100) needed to accept a brand
INGREDIENT_THRESHOLD = 90  # stricter: a wrong ingredient is worse than none
# Words printed after the ingredient name, e.g. "Metformin Hydrochloride IP"
SALT_WORDS = {"sodium", "potassium", "calcium", "magnesium", "hydrochloride", "hcl", "besylate",
              "besilate", "dihydrate", "trihydrate", "monohydrate", "ip", "bp", "usp"}
STRENGTH = re.compile(r"\b\d[\d,.]*\s*(?:mg|mcg|g|iu|ml)?\b", re.I)  # \b keeps the 3 in "D3"


@dataclass
class MatchResult:
    status: str  # ok | not_in_db | unreadable  (low_confidence comes with vision on Day 2)
    brand: str | None = None
    ingredients: list[str] = field(default_factory=list)  # drugs.json keys to explain
    unverified: list[str] = field(default_factory=list)   # on the pack, not in our DB
    score: float = 0.0


def match_brand(kb: KnowledgeBase, text: str) -> tuple[str | None, float]:
    key = norm(text)
    if not key:
        return None, 0.0
    if key in kb.alias_to_brand:
        return kb.alias_to_brand[key], 100.0
    hit = process.extractOne(key, kb.alias_to_brand.keys(), scorer=fuzz.ratio)
    if hit and hit[1] >= BRAND_THRESHOLD:
        return kb.alias_to_brand[hit[0]], hit[1]
    return None, hit[1] if hit else 0.0


def clean_ingredient(name: str) -> str:
    words = STRENGTH.sub(" ", name).lower().split()
    while len(words) > 1 and words[-1].strip(".,") in SALT_WORDS:
        words.pop()  # "Atorvastatin Calcium IP" -> "atorvastatin"
    return norm(" ".join(words))


def match_ingredient(kb: KnowledgeBase, name: str) -> str | None:
    key = clean_ingredient(name)
    if not key:
        return None
    if key in kb.name_to_drug:
        return kb.name_to_drug[key]
    hit = process.extractOne(key, kb.name_to_drug.keys(), scorer=fuzz.ratio)
    if hit and hit[1] >= INGREDIENT_THRESHOLD:
        return kb.name_to_drug[hit[0]]
    return None


def identify(kb: KnowledgeBase, brand_text: str | None, ingredient_names: list[str]) -> MatchResult:
    brand_text = (brand_text or "").strip()
    ingredient_names = [n for n in ingredient_names if n.strip()]
    if not brand_text and not ingredient_names:
        return MatchResult("unreadable")

    brand, score = match_brand(kb, brand_text)
    if brand:
        keys = [i["key"] for i in kb.brands[brand]["ingredients"]]
        return MatchResult("ok", brand, keys, score=score)

    known, unverified = [], []
    for n in ingredient_names:
        key = match_ingredient(kb, n)
        if key is None:
            unverified.append(n.strip())
        elif key not in known:
            known.append(key)
    status = "ok" if known else "not_in_db"
    return MatchResult(status, None, known, unverified, score)


def identify_text(kb: KnowledgeBase, query: str) -> MatchResult:
    """For a typed name: try it as a brand, then as one or more ingredients."""
    parts = re.split(r"\+|,|&|\band\b", query)
    return identify(kb, query, parts)
