# BrandVoice AI — Approach

## Brand voice analysis

The application collects the brand name, industry, campaign objective, product or service description, preferred tone, target audience, and optional instructions. Gemini first converts that brief into a structured brand profile containing personality, tone, audience, themes, writing style, and concise voice guidelines. User-provided context is treated as the primary source; the application does not claim to analyze live social posts unless they are supplied.

## Prompt design

Generation uses two focused prompts:

1. **Brand analysis** requests only the profile fields needed by the UI.
2. **Tweet generation** receives the validated profile and campaign context, then requests exactly ten JSON tweets with supported categories, unique ideas, exact character counts, and a 280-character limit.

The backend requests JSON from the official Google Gen AI SDK, rejects empty, truncated, malformed, incomplete, duplicate, or overlong responses, and returns a clear API error instead of silently substituting hardcoded content.

## Tools and technology

- React, Vite, Axios, and Lucide React for the interface.
- FastAPI, Pydantic v2, and `pydantic-settings` for the API.
- Google Gen AI Python SDK for Gemini.
- Pytest and FastAPI `TestClient` for mocked provider and API contract tests.
- Render and Vercel deployment configuration.

## Workflow

1. Validate and normalize the request at the FastAPI boundary.
2. Analyze the brand with Gemini.
3. Validate the returned brand profile.
4. Generate ten tweets using the validated profile.
5. Validate IDs, categories, uniqueness, lengths, and character counts.
6. Return the structured response to React.
7. Support copy, edit, individual regeneration, and regenerate-all without changing the API contract.

Provider failures are surfaced explicitly. Rate-limit or quota exhaustion is not retried; transient provider failures use bounded retries. Automated tests mock Gemini and therefore do not consume API quota.
