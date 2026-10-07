import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))  # so "import app" works

from app.config import settings
from app.kb import get_kb
from app.llm.gemini import LLMError, get_llm
from app.safety import SAFETY_ORDER, route

kb, llm = get_kb(), get_llm()
questions = json.loads((settings.data_dir / "redteam.json").read_text(encoding="utf-8"))["questions"]
class Recorder:
    """Wraps the real client so route() makes the only call, and we still see what Gemini said."""
    def __init__(self, llm):
        self.llm, self.last = llm, None

    def classify_question(self, question, drug_name):
        try:
            self.last = self.llm.classify_question(question, drug_name)
        except LLMError as e:
            self.last = "ERROR " + str(e)[:70]
            raise
        return self.last


rec = Recorder(llm)
unsafe = correct = errors = 0
for q in questions:
    brand = kb.brands.get(q["brand"] or "")
    drug = kb.drugs[brand["ingredients"][0]["key"]] if brand else None
    got = route(q["question"], drug, rec)
    errors += rec.last.startswith("ERROR")
    if got == q["expected"]:
        correct += 1
        continue
    kind = "UNSAFE" if SAFETY_ORDER.index(got) > SAFETY_ORDER.index(q["expected"]) else "SAFER "
    unsafe += kind == "UNSAFE"
    print(f"{kind} #{q['id']:>2}: expected {q['expected']:<16} got {got:<16} gemini: {rec.last} | {q['question']}")

print(f"\n{correct}/{len(questions)} exact, {unsafe} unsafe")
if errors:
    print(f"WARNING: Gemini failed on {errors}/{len(questions)} questions; this score is mostly the keyword layer.")
sys.exit(1 if unsafe else 0)
