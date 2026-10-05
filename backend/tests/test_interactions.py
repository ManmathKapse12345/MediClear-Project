import pytest

from app.interactions import Med, check
from app.kb import get_kb

kb = get_kb()


def med(brand):
    return Med(brand, tuple(i["key"] for i in kb.brands[brand]["ingredients"]))


def test_combination_brand_never_warns_about_itself():
    assert check(kb, [med("Telma-AM")]) == []


@pytest.mark.parametrize("pair", kb.interactions["pairs"], ids=lambda p: f"{p['a']}+{p['b']}")
def test_every_listed_pair_is_flagged(pair):
    alerts = check(kb, [Med("A", (pair["a"],)), Med("B", (pair["b"],))])
    assert [(a.kind, a.level) for a in alerts] == [("pair", pair["level"])]


def test_same_ingredient_in_two_brands():
    alerts = check(kb, [Med("Flexon 650", ("paracetamol",)), Med("Saridon", ("paracetamol",))])
    assert alerts[0].kind == "same_ingredient" and alerts[0].level == "warning"


def test_warnings_sorted_first():
    alerts = check(kb, [Med("A", ("ibuprofen",)), Med("B", ("telmisartan",)), Med("C", ("diclofenac",))])
    assert alerts[0].level == "warning"
