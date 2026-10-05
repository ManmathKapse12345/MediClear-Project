"""Interaction checks over a saved medicine list. No LLM: every alert comes from data/interactions.json."""
from dataclasses import dataclass
from itertools import combinations

from app.kb import KnowledgeBase

LEVEL_ORDER = {"warning": 0, "timing": 1, "caution": 2}


@dataclass(frozen=True)
class Med:
    label: str                    # brand name, or what the user saved it as
    ingredients: tuple[str, ...]  # drugs.json keys


@dataclass
class Alert:
    level: str
    kind: str                     # pair | same_ingredient | same_class
    between: tuple[str, str]
    ingredients: tuple[str, str]
    message: str
    sources: list[str]


def check(kb: KnowledgeBase, meds: list[Med]) -> list[Alert]:
    pairs = {frozenset((p["a"], p["b"])): p for p in kb.interactions["pairs"]}
    same_ing = kb.interactions["same_ingredient"]
    same_cls = kb.interactions["same_class"]
    alerts = []
    for m1, m2 in combinations(meds, 2):
        between = (m1.label, m2.label)
        seen_classes = set()
        for a in m1.ingredients:
            for b in m2.ingredients:
                if a == b:
                    drug = kb.drugs[a]
                    alerts.append(Alert(same_ing["level"], "same_ingredient", between, (a, b),
                                        same_ing["message"].replace("{ingredient}", drug["name"]),
                                        [drug["source"]] if drug["source"] else []))
                elif p := pairs.get(frozenset((a, b))):
                    alerts.append(Alert(p["level"], "pair", between, (a, b), p["message"], p["sources"]))
                else:
                    cls = kb.drugs[a]["class"]
                    if cls == kb.drugs[b]["class"] and cls in same_cls["classes"] and cls not in seen_classes:
                        seen_classes.add(cls)
                        alerts.append(Alert(same_cls["level"], "same_class", between, (a, b),
                                            same_cls["message"].replace("{class}", cls), []))
    return sorted(alerts, key=lambda x: LEVEL_ORDER[x.level])
