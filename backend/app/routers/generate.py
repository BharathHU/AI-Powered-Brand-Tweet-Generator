from functools import lru_cache

from fastapi import APIRouter, Depends

from app.config import get_settings
from app.schemas import (
    GenerationRequest, GenerationResponse, RegenerateRequest, RegenerateResponse,
)
from app.services.ai_service import AIService

router = APIRouter(prefix="/api")


@lru_cache
def get_ai_service() -> AIService:
    settings = get_settings()
    return AIService(settings)


@router.post("/generate", response_model=GenerationResponse)
def generate(
    request: GenerationRequest, service: AIService = Depends(get_ai_service)
) -> GenerationResponse:
    return service.generate(request)


@router.post("/regenerate/{tweet_id}", response_model=RegenerateResponse)
def regenerate(
    tweet_id: int, request: RegenerateRequest, service: AIService = Depends(get_ai_service)
) -> RegenerateResponse:
    request.tweet_id = tweet_id
    return RegenerateResponse(tweet=service.regenerate(request))


@router.post("/regenerate-all", response_model=GenerationResponse)
def regenerate_all(
    request: GenerationRequest, service: AIService = Depends(get_ai_service)
) -> GenerationResponse:
    return service.regenerate_all(request)
