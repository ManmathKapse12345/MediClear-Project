"""Loads the curated data once. These files are the only source of medical facts."""
import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from app.config import settings


def norm(s: str) -> str:
    """Same rule as data/check_data.py: lowercase, keep only a-z, 0-9 and '+'."""
    return re.sub(r"[^a-z0-9+]", "", s.lower())


# Other names printed on packs for ingredients we already have.
SYNONYMS = {
    "acetaminophen": "paracetamol",
    "thyroxine": "levothyroxine",
    "cholecalciferol": "vitamin_d3",
    "colecalciferol": "vitamin_d3",
    "acetylsalicylicacid": "aspirin",
}


@dataclass(frozen=True)
class KnowledgeBase:
    drugs: dict[str, dict]
    brands: dict[str, dict]
    interactions: dict
    alias_to_brand: dict[str, str]  # norm(alias) -> brand name
    name_to_drug: dict[str, str]    # norm(name)  -> drug key


def load_kb(data_dir: Path) -> KnowledgeBase:
    def load(name):
        return json.loads((data_dir / name).read_text(encoding="utf-8"))

    drugs = {d["key"]: d for d in load("drugs.json")}
    brands = load("brands.json")

    alias_to_brand = {}
    for brand, b in brands.items():
        for alias in [brand, *b["aliases"]]:
            alias_to_brand[norm(alias)] = brand

    name_to_drug = {norm(k): k for k in drugs} | {norm(d["name"]): k for k, d in drugs.items()}
    for alias, key in SYNONYMS.items():
        if key not in drugs:
            raise ValueError(f"synonym {alias} points to unknown drug {key}")
        name_to_drug[alias] = key

    return KnowledgeBase(drugs, brands, load("interactions.json"), alias_to_brand, name_to_drug)


@lru_cache
def get_kb() -> KnowledgeBase:
    return load_kb(settings.data_dir)
