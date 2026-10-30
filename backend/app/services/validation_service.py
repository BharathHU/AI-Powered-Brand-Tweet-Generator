from app.schemas import GenerationResponse


def validate_generation(payload: dict) -> GenerationResponse:
    return GenerationResponse.model_validate(payload)
