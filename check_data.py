"""Sanity-check the MediClear data files. Run: python check_data.py"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
load = lambda name: json.loads((ROOT / name).read_text(encoding="utf-8"))

drugs = load("drugs.json")
brands = load("brands.json")
interactions = load("interactions.json")
redteam = load("redteam.json")

errors = []
keys = {d["key"] for d in drugs}
classes = {d["class"] for d in drugs}

for d in drugs:
    if not d["no_trusted_source"]:
        for field in ("source", "used_for", "how_to_take"):
            if not d[field]:
                errors.append(f"drugs.json: {d['key']} has empty {field}")
        if not d["verified"]:
            errors.append(f"drugs.json: {d['key']} is not verified")

for name, b in brands.items():
    for ing in b["ingredients"]:
        if ing["key"] not in keys:
            errors.append(f"brands.json: {name} uses unknown ingredient {ing['key']}")

for p in interactions["pairs"]:
    for k in (p["a"], p["b"]):
        if k not in keys:
            errors.append(f"interactions.json: unknown ingredient {k}")
for c in interactions["same_class"]["classes"]:
    if c not in classes:
        errors.append(f"interactions.json: unknown class {c}")


def norm(s):
    return re.sub(r"[^a-z0-9+]", "", s.lower())


alias_to_brand = {}
for name, b in brands.items():
    for a in [name] + b["aliases"]:
        other = alias_to_brand.setdefault(norm(a), name)
        if other != name:
            errors.append(f"brands.json: alias '{a}' used by both {other} and {name}")

photos = sorted((ROOT / "test_photos").rglob("*.jpg"))
matched = 0
for p in photos:
    prefix = p.stem.split("_")[0]
    if norm(prefix) in alias_to_brand:
        matched += 1
    else:
        errors.append(f"test_photos: {p.name} prefix '{prefix}' matches no brand alias")

own_dir = ROOT / "test_photos_own"
own = json.loads((own_dir / "expected.json").read_text(encoding="utf-8"))["photos"]
statuses = {"ok", "unreadable", "low_confidence", "not_in_db", "error"}
for fname, exp in own.items():
    if not (own_dir / fname).exists():
        errors.append(f"test_photos_own: {fname} listed in expected.json but missing")
    if not exp["accept"] or not set(exp["accept"]) <= statuses:
        errors.append(f"test_photos_own: {fname} has invalid accept {exp['accept']}")
    for k in exp["ingredients"]:
        if k not in keys:
            errors.append(f"test_photos_own: {fname} uses unknown ingredient {k}")
    if norm(fname.split("_")[0]) in alias_to_brand:
        errors.append(f"test_photos_own: {fname} is a known brand; own photos should test unknown brands")
for p in own_dir.glob("*.jpg"):
    if p.name not in own:
        errors.append(f"test_photos_own: {p.name} has no entry in expected.json")

missing_how =[d["key"] for d in drugs if not d["no_trusted_source"] and not d["how_it_works"]]

print(f"drugs: {len(drugs)}  brands: {len(brands)}  interaction pairs: {len(interactions['pairs'])}  red-team questions: {len(redteam['questions'])}")
print(f"photos matched to a brand: {matched}/{len(photos)}")
print(f"own photos with expected results: {len(own)}")
print(f"entries with no how_it_works (source does not explain it): {missing_how or 'none'}")
print("ERRORS:" if errors else "All checks passed.")
for e in errors:
    print("  -", e)
