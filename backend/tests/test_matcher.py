import pytest

from app.kb import get_kb
from app.matcher import clean_ingredient, identify, identify_text, match_ingredient

kb = get_kb()


def test_every_alias_resolves_to_its_brand():
    for brand, b in kb.brands.items():
        for alias in [brand, *b["aliases"]]:
            assert identify_text(kb, alias).brand == brand, alias


def test_fuzzy_brand_tolerates_ocr_slip():
    assert identify(kb, "Amlip-S", []).brand == "Amlip-5"


@pytest.mark.parametrize("printed,key", [
    ("Atorvastatin Calcium IP 40 mg", "atorvastatin"),
    ("Metformin Hydrochloride IP", "metformin"),
    ("Levothyroxine Sodium", "levothyroxine"),
    ("Calcium Carbonate", "calcium"),
    ("Cholecalciferol 60,000 IU", "vitamin_d3"),
    ("Paracetamol (Anhydrous) IP 500 mg", "paracetamol"),
])
def test_ingredient_names_on_packs(printed, key):
    assert match_ingredient(kb, printed) == key


def test_unknown_brand_with_known_ingredient():  # Saridon strip back
    r = identify(kb, "Saridon", ["Paracetamol IP 500 mg", "Caffeine IP 50 mg"])
    assert (r.status, r.brand, r.ingredients) == ("ok", None, ["paracetamol"])
    assert "caffeine" in r.unverified[0].lower()


def test_bracketed_qualifier_is_ignored():  # Saridon back prints "Caffeine (Anhydrous)"
    assert clean_ingredient("Caffeine (Anhydrous) IP 50 mg") == "caffeine"


def test_unknown_brand_alone_is_not_guessed():  # Saridon strip front
    assert identify(kb, "Saridon", []).status == "not_in_db"


def test_homeopathic_not_in_db():
    assert identify(kb, "Calcarea Phosphorica 6X", ["Calcarea Phosphorica"]).status == "not_in_db"


def test_nothing_readable():
    assert identify(kb, "", []).status == "unreadable"
