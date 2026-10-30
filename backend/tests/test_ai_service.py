import json

import pytest
from fastapi import HTTPException

from app.config import Settings
from app.services.ai_service import AIService


class FakeModels:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = 0

    def generate_content(self, **kwargs):
        self.calls += 1
        response = next(self.responses)
        if isinstance(response, Exception):
            raise response
        return response


class FakeClient:
    def __init__(self, responses):
        self.models = FakeModels(responses)


class FakeResponse:
    def __init__(self, text):
        self.text = text
        self.candidates = []


def service_with(responses):
    service = AIService(Settings(gemini_api_key="test-key"))
    client = FakeClient(responses)
    service._client_instance = client
    return service, client


def test_invalid_json_is_rejected_without_retry():
    service, client = service_with([
        FakeResponse("{not json"),
    ])
    with pytest.raises(HTTPException) as error:
        service._generate_json("prompt")
    assert error.value.status_code == 502
    assert client.models.calls == 1


def test_transient_provider_error_retries():
    service, client = service_with([
        TimeoutError("deadline exceeded"),
        FakeResponse("{}"),
    ])
    assert service._generate_json("prompt") == {}
    assert client.models.calls == 2


def test_permanent_provider_error_does_not_retry():
    service, client = service_with([RuntimeError("invalid api key")])
    with pytest.raises(HTTPException) as error:
        service._generate_json("prompt")
    assert error.value.status_code == 502
    assert client.models.calls == 1


def test_empty_provider_response_is_rejected_without_retry():
    service, client = service_with([FakeResponse("")])
    with pytest.raises(HTTPException) as error:
        service._generate_json("prompt")
    assert error.value.status_code == 502
    assert client.models.calls == 1


def test_truncated_provider_response_is_rejected():
    response = FakeResponse('{"tweets":')
    response.candidates = [type("Candidate", (), {"finish_reason": "MAX_TOKENS"})()]
    service, client = service_with([response])
    with pytest.raises(HTTPException) as error:
        service._generate_json("prompt")
    assert error.value.status_code == 502
    assert client.models.calls == 1


def test_provider_status_mapping_preserves_client_error_codes():
    assert AIService._provider_error_status(400)[0] == 400
    assert AIService._provider_error_status(401)[0] == 401
    assert AIService._provider_error_status(403)[0] == 403
    assert AIService._provider_error_status(429)[0] == 429
