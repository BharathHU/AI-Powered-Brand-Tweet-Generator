
import json
import logging
import re
import time
from typing import Any

from fastapi import HTTPException, status
from pydantic import ValidationError

from app.config import Settings
from app.schemas import (
    BrandProfile,
    GenerationRequest,
    GenerationResponse,
    RegenerateRequest,
    Tweet,
)
from app.services.prompt_service import (
    brand_analysis_prompt,
    tweet_generation_prompt,
)
from app.services.validation_service import validate_generation

logger = logging.getLogger(__name__)


class AIService:
    """Gemini integration with controlled retries and response validation."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._client_instance: Any | None = None

    def _client(self) -> Any:
        """Create and reuse a Gemini client."""

        if not self.settings.gemini_api_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Gemini API key is not configured.",
            )

        if self._client_instance is not None:
            return self._client_instance

        try:
            from google import genai
            from google.genai import types

            self._client_instance = genai.Client(
                api_key=self.settings.gemini_api_key,
                http_options=types.HttpOptions(
                    timeout=int(
                        self.settings.request_timeout_seconds * 1000
                    )
                ),
            )

            return self._client_instance

        except ImportError as exc:
            raise HTTPException(
                status_code=503,
                detail="Gemini SDK is unavailable.",
            ) from exc

    @staticmethod
    def _strip_json_fence(raw_text: str) -> str:
        """Remove Markdown JSON fences if Gemini includes them."""

        match = re.fullmatch(
            r"\s*```(?:json)?\s*(.*?)\s*```\s*",
            raw_text,
            re.DOTALL | re.IGNORECASE,
        )

        return match.group(1).strip() if match else raw_text.strip()

    @staticmethod
    def _is_incomplete(response: Any) -> bool:
        """Check whether Gemini stopped because of the token limit."""

        candidates = getattr(response, "candidates", None) or []

        if not candidates:
            return False

        reason = str(
            getattr(candidates[0], "finish_reason", "")
        ).upper()

        return "MAX_TOKENS" in reason or "LENGTH" in reason

    @staticmethod
    def _is_retryable(exc: Exception) -> bool:
        """Retry temporary failures, never quota exhaustion."""

        try:
            from google.genai import errors

            if isinstance(exc, errors.ClientError):
                # Includes 429 quota and rate-limit responses.
                return False

            if isinstance(exc, errors.ServerError):
                return getattr(exc, "code", None) in (500, 502, 503, 504)

        except ImportError:
            pass

        name = type(exc).__name__.lower()
        message = str(exc).lower()

        transient_markers = (
            "timeout",
            "deadline_exceeded",
            "connectionerror",
            "connectionreset",
            "temporarily unavailable",
            "service unavailable",
        )

        return any(
            marker in name or marker in message
            for marker in transient_markers
        )

    @staticmethod
    def _provider_error_status(code: int | None) -> tuple[int, str]:
        if code == 400:
            return 400, "Gemini rejected the generation request."
        if code in (401, 403):
            return code, "Gemini API authentication or permission error."
        if code == 429:
            return 429, (
                "Gemini API quota or rate limit exceeded. "
                "Check your usage and billing, or wait for the quota to reset."
            )
        return 502, "Gemini provider request failed. Please try again."

    def _generate_json(
        self,
        prompt: str,
        max_output_tokens: int = 2048,
    ) -> dict:
        """Generate JSON with limited retries for temporary failures."""

        from google.genai import types, errors

        client = self._client()

        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=self.settings.gemini_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.4,
                        max_output_tokens=max_output_tokens,
                    ),
                )

                raw_text = (
                    getattr(response, "text", None) or ""
                ).strip()

                if not raw_text:
                    raise HTTPException(
                        status_code=502,
                        detail="Gemini returned an empty response.",
                    )

                if self._is_incomplete(response):
                    raise HTTPException(
                        status_code=502,
                        detail=(
                            "Gemini response was truncated. "
                            "Try reducing the requested output."
                        ),
                    )

                raw_text = self._strip_json_fence(raw_text)

                try:
                    result = json.loads(raw_text)
                except json.JSONDecodeError as exc:
                    logger.error(
                        "Gemini returned invalid JSON at position %s",
                        exc.pos,
                    )
                    raise HTTPException(
                        status_code=502,
                        detail="Gemini returned invalid JSON.",
                    ) from exc

                if not isinstance(result, dict):
                    raise HTTPException(
                        status_code=502,
                        detail="Gemini did not return a JSON object.",
                    )

                return result

            except HTTPException:
                raise

            except errors.ClientError as exc:
                provider_status, detail = self._provider_error_status(
                    getattr(exc, "code", None)
                )
                logger.error("Gemini client error with status %s", provider_status)
                raise HTTPException(
                    status_code=provider_status,
                    detail=detail,
                ) from exc

            except Exception as exc:
                if attempt == 0 and self._is_retryable(exc):
                    logger.warning(
                        "Temporary Gemini error. Retrying once: %s",
                        exc,
                    )
                    time.sleep(0.5)
                    continue

                logger.exception("Gemini provider request failed")

                raise HTTPException(
                    status_code=504 if self._is_retryable(exc) else 502,
                    detail="Gemini provider request failed. Please try again.",
                ) from exc

        raise HTTPException(
            status_code=502,
            detail="Gemini response could not be generated.",
        )

    @staticmethod
    def _normalize_profile_data(
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Normalize list fields returned by Gemini."""

        normalized = data.copy()

        for field, maximum in {
            "content_themes": 8,
            "voice_summary": 4,
        }.items():

            value = normalized.get(field)

            if isinstance(value, str):
                value = re.split(r"[\n,]+", value)

            if isinstance(value, list):
                normalized[field] = [
                    str(item).strip(" -*•\t")
                    for item in value
                    if str(item).strip()
                ][:maximum]

        return normalized

    def generate(
        self,
        request: GenerationRequest,
    ) -> GenerationResponse:
        """Generate a brand profile and exactly ten tweets."""

        started = time.perf_counter()

        # STEP 1: Brand analysis.
        logger.info("Starting brand analysis")

        profile_started = time.perf_counter()

        profile_data = self._generate_json(
            brand_analysis_prompt(request),
            max_output_tokens=768,
        )

        profile_data = self._normalize_profile_data(profile_data)

        profile_data.update({
            "brand_name": request.brand_name or "Your brand",
            "industry": request.industry or "General",
        })

        try:
            profile = BrandProfile.model_validate(profile_data)

        except ValidationError as exc:
            logger.exception("Brand profile validation failed")

            raise HTTPException(
                status_code=502,
                detail="Gemini returned an invalid brand profile.",
            ) from exc

        logger.info(
            "Brand analysis completed in %.2f seconds",
            time.perf_counter() - profile_started,
        )

        # STEP 2: Tweet generation.
        logger.info("Starting tweet generation")

        tweet_started = time.perf_counter()

        tweet_data = self._generate_json(
            tweet_generation_prompt(profile, request),
            max_output_tokens=3072,
        )

        logger.info(
            "Tweet generation completed in %.2f seconds",
            time.perf_counter() - tweet_started,
        )

        # STEP 3: Validate final response.
        try:
            result = validate_generation({
                "brand_profile": profile.model_dump(),
                "tweets": tweet_data.get("tweets", []),
            })

        except (ValidationError, ValueError) as exc:
            logger.exception("Tweet validation failed")

            raise HTTPException(
                status_code=502,
                detail="Generated tweets failed validation.",
            ) from exc

        logger.info(
            "Total generation completed in %.2f seconds",
            time.perf_counter() - started,
        )

        return result

    def regenerate(
        self,
        request: RegenerateRequest,
    ) -> Tweet:
        """Regenerate one tweet."""

        prompt = f"""
Generate one original {request.category} tweet.

Brand profile:
{request.brand_profile.model_dump_json()}

Campaign objective: {request.campaign_objective}
Product: {request.product_description}
Additional instructions: {request.additional_instructions or "None"}

Return only valid JSON with:
- id: {request.tweet_id}
- category: "{request.category}"
- text
- character_count

Maximum length: 280 characters.
Character count must exactly match the text length.
Avoid unsupported claims.
"""

        tweet_data = self._generate_json(
            prompt,
            max_output_tokens=384,
        )

        try:
            return Tweet.model_validate(tweet_data)

        except ValidationError as exc:
            logger.exception("Regenerated tweet validation failed")

            raise HTTPException(
                status_code=502,
                detail="Regenerated tweet failed validation.",
            ) from exc

    def regenerate_all(
        self,
        request: GenerationRequest,
    ) -> GenerationResponse:
        """Generate a fresh brand profile and all ten tweets."""

        return self.generate(request)
