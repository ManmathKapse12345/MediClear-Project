"""Thin Gemini wrapper. The LLM reads packs and rephrases DB facts; it never decides what is true."""
import json
from functools import lru_cache
from typing import Literal

import httpx
from google import genai
from google.genai import errors, types
from pydantic import BaseModel

from app.config import settings
from app.llm import prompts

Label = Literal["refuse_to_doctor", "emergency_112", "answer_from_db", "not_in_db", "stay_in_scope"]
# Only these drugs.json fields go to the LLM: no URLs, no verification metadata
FACT_FIELDS = ("name", "used_for", "how_it_works", "how_to_take", "common_side_effects", "serious_warnings", "avoid")


class VisionIngredient(BaseModel):
    name: str
    strength: str | None = None


class VisionResult(BaseModel):
    readable: bool
    brand_text: str | None = None
    ingredients: list[VisionIngredient] = []
    confidence: float


class ExplainResult(BaseModel):
    used_for: str
    how_it_works: str
    how_to_take: str
    avoid: list[str]
    side_effects: list[str]
    see_doctor_if: list[str]


class Classification(BaseModel):
    label: Label


class LLMError(Exception):
    """Gemini failed after retries, or returned something unusable."""


class GeminiClient:
    # def __init__(self, api_key: str, model: str, timeout_s: int = 30, fallback_model: str | None = None):
    #     if not api_key:
    #         raise LLMError("GEMINI_API_KEY is not set")
    #     self.model = model
    #     self.client = genai.Client(api_key=api_key, http_options=types.HttpOptions(
    #         timeout=timeout_s * 1000,  # milliseconds
    #         retry_options=types.HttpRetryOptions(attempts=3, initial_delay=1.0),  # retries 408/429/5xx with backoff
    #     ))
    #     self.models = [model] + ([fallback_model] if fallback_model else [])
    def __init__(self, api_key: str, model: str, timeout_s: int = 30, fallback_model: str | None = None):
        self.models = [model] + ([fallback_model] if fallback_model else [])
        self.client = genai.Client(api_key=api_key, http_options=types.HttpOptions(
            timeout=timeout_s * 1000,  # milliseconds
            retry_options=types.HttpRetryOptions(attempts=3, initial_delay=1.0),  # retries 408/429/5xx with backoff
        )) if api_key else None


    def _generate(self, contents, schema: type[BaseModel]):
        if self.client is None:
            raise LLMError("GEMINI_API_KEY is not set")
        config = types.GenerateContentConfig(
            response_mime_type="application/json", response_schema=schema, temperature=0,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True))

        for i, model in enumerate(self.models):
            try:
                resp = self.client.models.generate_content(model=model, contents=contents, config=config)
                break
            except errors.APIError as e:
                # 5xx = model busy; 429 = this model's quota is used up. Both: try the next model.
                retryable = isinstance(e, errors.ServerError) or e.code == 429
                if not retryable or i == len(self.models) - 1:
                    raise LLMError(f"Gemini request failed: {e}") from e
            except httpx.HTTPError as e:
                raise LLMError(f"Gemini request failed: {e}") from e

        if resp.parsed is None:
            raise LLMError("Gemini returned no valid JSON")
        return resp.parsed

    def vision_extract(self, image: bytes, mime_type: str) -> VisionResult:
        return self._generate([types.Part.from_bytes(data=image, mime_type=mime_type), prompts.VISION], VisionResult)

    def explain(self, drug: dict, lang: str) -> ExplainResult:
        facts = json.dumps({k: drug[k] for k in FACT_FIELDS}, ensure_ascii=False, indent=1)
        return self._generate(prompts.EXPLAIN.format(language=prompts.LANGUAGES[lang], facts=facts), ExplainResult)

    def classify_question(self, question: str, drug_name: str | None) -> Label:
        prompt = prompts.CLASSIFY.format(question=question, drug=drug_name or "unknown")
        return self._generate(prompt, Classification).label


@lru_cache
def get_llm() -> GeminiClient:
    # return GeminiClient(settings.gemini_api_key, settings.gemini_model, settings.gemini_timeout_s)
    return GeminiClient(settings.gemini_api_key, settings.gemini_model, settings.gemini_timeout_s,
                        settings.gemini_fallback_model)
