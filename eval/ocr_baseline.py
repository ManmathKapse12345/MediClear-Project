"""Photo eval: runs the real photo pipeline on test_photos_own/ and compares with expected.json.

Calls the real Gemini (about one request per photo), so it is not part of pytest or CI.
Run from the project root:  python eval/ocr_baseline.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))  # so "import app" works

from app.kb import get_kb
from app.llm.gemini import LLMError, get_llm
from app.matcher import clean_ingredient
from app.pipeline import identify_photo

PHOTOS = ROOT / "test_photos_own"
MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}



def same_names(got: list[str], want: list[str]) -> bool:
    """Cleaned like the app does, and contained, so "Calcarea Phosphorica 6X" counts as "calcarea phosphorica"."""
    got_clean = [clean_ingredient(g) for g in got]
    return len(got) == len(want) and all(any(clean_ingredient(w) in g for g in got_clean) for w in want)


sys.stdout.reconfigure(encoding="utf-8")  # ✓/✗ crash older Windows consoles otherwise
kb, llm = get_kb(), get_llm()
expected = json.loads((PHOTOS / "expected.json").read_text(encoding="utf-8"))["photos"]

correct = wrong_ok = errors = 0
for name, exp in expected.items():
    path = PHOTOS / name
    try:
        r = identify_photo(kb, llm, path.read_bytes(), MIME[path.suffix.lower()])
        status, ingredients, unverified, reasons = r.status, set(r.ingredients), r.unverified, r.reasons
    except LLMError as e:
        errors += 1
        status, ingredients, unverified, reasons = "error", set(), [], [str(e)[:70]]

    problems = []
    if status not in exp["accept"]:
        problems.append(f"status {status}, expected {'/'.join(exp['accept'])}")
    if ingredients != set(exp["ingredients"]):
        problems.append(f"ingredients {sorted(ingredients)}, expected {exp['ingredients']}")
    if not same_names(unverified, exp["unverified"]):
        problems.append(f"unverified {unverified}, expected {exp['unverified']}")
    # the worst failure: confidently explaining the wrong medicine
    if status == "ok" and ingredients != set(exp["ingredients"]):
        wrong_ok += 1
        problems.insert(0, "WRONG OK")

    correct += not problems
    mark = "✓" if not problems else "✗"
    detail = "; ".join(problems) if problems else status
    print(f"{mark} {name:<42} {detail}" + (f"  (reasons: {' '.join(reasons)})" if reasons else ""))

print(f"\n{correct}/{len(expected)} correct, {wrong_ok} wrong ok")
if errors:
    print(f"WARNING: Gemini failed on {errors}/{len(expected)} photos; those count as wrong.")
sys.exit(1 if wrong_ok else 0)
