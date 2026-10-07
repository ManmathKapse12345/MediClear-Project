import pytest
from gtts import gTTSError

from app import tts
from app.explain import NO_SOURCE_TEXT
from app.tts import TTSError


@pytest.fixture
def fake_tts(monkeypatch):
    calls = []

    def synth(text, lang):
        calls.append((text, lang))
        return b"mp3"
    monkeypatch.setattr(tts, "synthesize", synth)  # tests never touch the network
    return calls


def test_returns_mp3_and_caches_it(client, fake_llm, fake_tts):
    for _ in range(2):
        r = client.get("/api/audio/paracetamol?lang=en")
        assert r.status_code == 200 and r.headers["content-type"] == "audio/mpeg" and r.content == b"mp3"
    assert len(fake_tts) == 1


def test_speaks_the_translated_explanation(client, fake_llm, fake_tts):
    client.get("/api/audio/paracetamol?lang=hi")
    text, lang = fake_tts[0]
    assert lang == "hi" and "[hi]" in text  # FakeLLM marks its translations with [hi]


def test_no_trusted_source_speaks_the_fixed_message(client, fake_llm, fake_tts):
    client.get("/api/audio/serratiopeptidase?lang=mr")
    assert NO_SOURCE_TEXT["mr"] in fake_tts[0][0]


def test_tts_failure_is_503_and_caches_nothing(client, fake_llm, monkeypatch):
    def boom(text, lang):
        raise TTSError("down")
    monkeypatch.setattr(tts, "synthesize", boom)
    assert client.get("/api/audio/paracetamol").status_code == 503


def test_gtts_error_becomes_tts_error(monkeypatch):
    class Broken:
        def __init__(self, text, lang):
            pass

        def write_to_fp(self, fp):
            raise gTTSError("no network")
    monkeypatch.setattr(tts, "gTTS", Broken)
    with pytest.raises(TTSError):
        tts.synthesize("hello", "en")


def test_unknown_drug_or_language(client, fake_llm, fake_tts):
    assert client.get("/api/audio/madeup").status_code == 404
    assert client.get("/api/audio/paracetamol?lang=fr").status_code == 422
