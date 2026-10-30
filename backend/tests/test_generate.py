from fastapi.testclient import TestClient

from app.main import app
from app.routers.generate import get_ai_service
from app.services.ai_service import AIService
from app.config import Settings
from app.schemas import GenerationResponse

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_missing_product_description():
    response = client.post("/api/generate", json={"campaign_objective": "Engagement"})
    assert response.status_code == 422


def test_missing_api_key_is_explicit():
    app.dependency_overrides[get_ai_service] = lambda: AIService(Settings(gemini_api_key=""))
    try:
        response = client.post("/api/generate", json={
            "campaign_objective": "Engagement",
            "product_description": "A useful product for creative teams.",
        })
        assert response.status_code == 503
    finally:
        app.dependency_overrides.clear()


def valid_request() -> dict:
    return {
        "brand_name": "Northstar Coffee",
        "industry": "Specialty coffee",
        "campaign_objective": "Engagement",
        "product_description": "Small-batch coffee for curious mornings.",
        "preferred_tone": "Friendly",
        "target_audience": "",
        "additional_instructions": "",
    }


class FakeAIService:
    def generate(self, request):
        categories = (
            ["Conversational"] * 2
            + ["Promotional"] * 2
            + ["Witty / Meme-style"] * 2
            + ["Informative"] * 2
            + ["Engagement", "Community-focused"]
        )
        tweets = [
            {
                "id": index,
                "category": categories[index - 1],
                "text": f"Fresh coffee thought number {index}.",
                "character_count": len(f"Fresh coffee thought number {index}."),
            }
            for index in range(1, 11)
        ]
        return GenerationResponse(
            brand_profile={
                "brand_name": request.brand_name or "Your brand",
                "industry": request.industry or "General",
                "personality": "Warm",
                "tone": request.preferred_tone,
                "target_audience": request.target_audience or "Coffee lovers",
                "content_themes": ["Coffee", "Ritual"],
                "writing_style": "Conversational",
                "voice_summary": ["Warm", "Curious", "Inviting"],
            },
            tweets=tweets,
        )

    def regenerate(self, request):
        text = f"Fresh replacement for tweet {request.tweet_id}."
        return {
            "id": request.tweet_id,
            "category": request.category,
            "text": text,
            "character_count": len(text),
        }

    def regenerate_all(self, request):
        return self.generate(request)


def test_valid_generate_request_accepts_frontend_payload():
    app.dependency_overrides[get_ai_service] = lambda: FakeAIService()
    try:
        response = client.post("/api/generate", json=valid_request())
        assert response.status_code == 200
        assert len(response.json()["tweets"]) == 10
    finally:
        app.dependency_overrides.clear()


def test_short_product_description_returns_field_error():
    payload = valid_request()
    payload["product_description"] = "Too short"
    response = client.post("/api/generate", json=payload)
    assert response.status_code == 422
    assert any(error["field"] == "product_description" for error in response.json()["errors"])


def test_nullable_optional_fields_are_normalized():
    payload = valid_request()
    payload.update({
        "brand_name": None,
        "industry": None,
        "preferred_tone": None,
        "target_audience": None,
    })
    app.dependency_overrides[get_ai_service] = lambda: FakeAIService()
    try:
        assert client.post("/api/generate", json=payload).status_code == 200
    finally:
        app.dependency_overrides.clear()


def test_regenerate_tweet_contract():
    app.dependency_overrides[get_ai_service] = lambda: FakeAIService()
    payload = {
        "brand_profile": {
            "brand_name": "Northstar Coffee",
            "industry": "Coffee",
            "personality": "Warm",
            "tone": "Friendly",
            "target_audience": "Coffee lovers",
            "content_themes": ["Coffee"],
            "writing_style": "Conversational",
            "voice_summary": ["Warm", "Curious", "Inviting"],
        },
        "campaign_objective": "Engagement",
        "product_description": "Small-batch coffee for curious mornings.",
        "category": "Conversational",
        "tweet_id": 3,
    }
    try:
        response = client.post("/api/regenerate/3", json=payload)
        assert response.status_code == 200
        assert response.json()["tweet"]["id"] == 3
    finally:
        app.dependency_overrides.clear()


def test_regenerate_all_contract():
    app.dependency_overrides[get_ai_service] = lambda: FakeAIService()
    try:
        response = client.post("/api/regenerate-all", json=valid_request())
        assert response.status_code == 200
        assert len(response.json()["tweets"]) == 10
    finally:
        app.dependency_overrides.clear()
