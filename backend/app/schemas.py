from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

CAMPAIGN_OBJECTIVES = {
    "Engagement", "Product Promotion", "Brand Awareness", "Lead Generation",
    "Product Launch", "Community Building",
}
TONES = {
    "Witty", "Premium", "Humorous", "Informative", "Bold", "Minimal",
    "Professional", "Friendly", "Inspirational", "Let AI Decide",
}
CATEGORIES = {
    "Conversational", "Promotional", "Witty / Meme-style", "Informative",
    "Engagement", "Community-focused",
}


class GenerationRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    brand_name: Annotated[str, Field(default="", max_length=120)]
    industry: Annotated[str, Field(default="", max_length=160)]
    campaign_objective: str
    product_description: Annotated[str, Field(min_length=10, max_length=2000)]
    preferred_tone: Annotated[str, Field(default="Let AI Decide")]
    target_audience: Annotated[str, Field(default="", max_length=300)]
    additional_instructions: Annotated[str, Field(default="", max_length=1000)]

    @field_validator(
        "brand_name", "industry", "preferred_tone", "target_audience",
        "additional_instructions", mode="before",
    )
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str:
        return "" if value is None else value

    @field_validator("product_description", mode="before")
    @classmethod
    def require_product_description(cls, value: str | None) -> str:
        if value is None or not isinstance(value, str) or not value.strip():
            raise ValueError("Product/service description is required.")
        return value

    @field_validator("campaign_objective")
    @classmethod
    def valid_objective(cls, value: str) -> str:
        if value not in CAMPAIGN_OBJECTIVES:
            raise ValueError(
                f"Invalid campaign objective '{value}'. "
                f"Choose one of: {', '.join(sorted(CAMPAIGN_OBJECTIVES))}."
            )
        return value

    @field_validator("preferred_tone")
    @classmethod
    def valid_tone(cls, value: str) -> str:
        if not value:
            return "Let AI Decide"
        if value not in TONES:
            raise ValueError(
                f"Invalid preferred tone '{value}'. "
                f"Choose one of: {', '.join(sorted(TONES))}."
            )
        return value


class BrandProfile(BaseModel):
    brand_name: Annotated[str, Field(min_length=1)]
    industry: Annotated[str, Field(min_length=1)]
    personality: Annotated[str, Field(min_length=1)]
    tone: Annotated[str, Field(min_length=1)]
    target_audience: Annotated[str, Field(min_length=1)]
    content_themes: list[str] = Field(min_length=1, max_length=8)
    writing_style: str
    voice_summary: list[str] = Field(min_length=3, max_length=4)


class Tweet(BaseModel):
    id: int = Field(ge=1)
    category: str
    text: str = Field(min_length=1, max_length=280)
    character_count: int = Field(ge=1, le=280)

    @field_validator("category")
    @classmethod
    def valid_category(cls, value: str) -> str:
        if value not in CATEGORIES:
            raise ValueError("Invalid tweet category.")
        return value

    def model_post_init(self, __context: object) -> None:
        if self.character_count != len(self.text):
            raise ValueError("character_count must match tweet text length.")


class GenerationResponse(BaseModel):
    brand_profile: BrandProfile
    tweets: list[Tweet] = Field(min_length=10, max_length=10)

    @field_validator("tweets")
    @classmethod
    def unique_tweets(cls, value: list[Tweet]) -> list[Tweet]:
        if len({tweet.text.casefold() for tweet in value}) != 10:
            raise ValueError("Tweets must be unique.")
        if sorted(tweet.id for tweet in value) != list(range(1, 11)):
            raise ValueError("Tweet IDs must contain exactly 1 through 10.")
        counts = {category: sum(tweet.category == category for tweet in value) for category in CATEGORIES}
        required_categories = {
            "Conversational", "Promotional", "Witty / Meme-style", "Informative",
        }
        missing = [category for category in required_categories if counts[category] < 2]
        if missing:
            raise ValueError(
                "Tweet set needs at least two tweets in each core category: "
                + ", ".join(sorted(missing))
            )
        if counts["Engagement"] + counts["Community-focused"] < 2:
            raise ValueError(
                "Tweet set needs at least two Engagement or Community-focused tweets."
            )
        return value


class RegenerateRequest(BaseModel):
    brand_profile: BrandProfile
    campaign_objective: str
    product_description: Annotated[str, Field(min_length=10, max_length=2000)]
    additional_instructions: Annotated[str, Field(default="", max_length=1000)]
    category: str = "Conversational"
    tweet_id: int = Field(ge=1)

    @field_validator("category")
    @classmethod
    def valid_regeneration_category(cls, value: str) -> str:
        if value not in CATEGORIES:
            raise ValueError("Invalid tweet category.")
        return value


class RegenerateResponse(BaseModel):
    tweet: Tweet
