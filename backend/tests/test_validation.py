import pytest
from pydantic import ValidationError

from app.schemas import GenerationResponse


def tweet(number: int, text: str = "A unique tweet") -> dict:
    return {
        "id": number, "category": "Conversational", "text": f"{text} {number}",
        "character_count": len(f"{text} {number}"),
    }


def profile() -> dict:
    return {
        "brand_name": "Test", "industry": "Software", "personality": "Bright",
        "tone": "Friendly", "target_audience": "Teams", "content_themes": ["Growth"],
        "writing_style": "Clear", "voice_summary": ["Warm", "Clear", "Useful"],
    }


def test_requires_exactly_ten_unique_tweets():
    with pytest.raises(ValidationError):
        GenerationResponse(brand_profile=profile(), tweets=[tweet(1)] * 10)


def test_rejects_tweet_over_280_characters():
    long_text = "x" * 281
    with pytest.raises(ValidationError):
        GenerationResponse(
            brand_profile=profile(),
            tweets=[tweet(i, long_text) for i in range(1, 11)],
        )
