import pytest
from pydantic import ValidationError

from app.schemas import GenerationResponse


def tweet(number: int, category: str, text: str = "A unique tweet") -> dict:
    return {
        "id": number, "category": category, "text": f"{text} {number}",
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
        GenerationResponse(
            brand_profile=profile(),
            tweets=[tweet(1, "Conversational")] * 10,
        )


def test_rejects_tweet_over_280_characters():
    long_text = "x" * 281
    with pytest.raises(ValidationError):
        GenerationResponse(
            brand_profile=profile(),
            tweets=[
                tweet(
                    i,
                    ["Conversational", "Promotional", "Witty / Meme-style", "Informative"][(i - 1) % 4],
                    long_text,
                )
                for i in range(1, 11)
            ],
        )


def balanced_tweets() -> list[dict]:
    categories = (
        ["Conversational"] * 2
        + ["Promotional"] * 2
        + ["Witty / Meme-style"] * 2
        + ["Informative"] * 2
        + ["Engagement", "Community-focused"]
    )
    return [tweet(index, category) for index, category in enumerate(categories, 1)]


def test_requires_balanced_core_categories():
    tweets = balanced_tweets()
    tweets[2]["category"] = "Conversational"
    with pytest.raises(ValidationError, match="core category"):
        GenerationResponse(brand_profile=profile(), tweets=tweets)


def test_accepts_balanced_category_mix():
    response = GenerationResponse(
        brand_profile=profile(),
        tweets=balanced_tweets(),
    )
    assert len(response.tweets) == 10
