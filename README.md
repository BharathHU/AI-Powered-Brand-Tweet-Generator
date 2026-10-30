# BrandVoice AI

BrandVoice AI turns a brand brief into a brand voice profile and exactly ten distinct X/Twitter posts. Voice is inferred from user-provided context and Gemini's general knowledge; the app does not claim to analyze live social posts unless posts are supplied.

## Stack and architecture

- Frontend: React, Vite, Axios, Lucide React, and CSS.
- Backend: FastAPI, Pydantic v2, `python-dotenv`, `pydantic-settings`, and the official `google-genai` SDK.
- AI flow: two bounded Gemini calls (brand analysis, then tweet generation). The reusable service client and concise prompts reduce setup and output overhead while preserving validation quality.
- Pydantic enforces exactly 10 tweets, IDs 1-10, supported categories, unique text, exact character counts, and the 280-character limit.

## Prerequisites

Use Python 3.11+ and Node.js 18+. A Gemini API key is required for live generation.

## Windows PowerShell setup

```powershell
cd "C:\Users\bhara\OneDrive\Desktop\BrandVoice AI — AI-Powered Brand Tweet Generator\backend"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
# Edit .env and set GEMINI_API_KEY and GEMINI_MODEL.
python -m uvicorn app.main:app --reload
```

In another PowerShell window:

```powershell
cd "C:\Users\bhara\OneDrive\Desktop\BrandVoice AI — AI-Powered Brand Tweet Generator\frontend"
npm install
Copy-Item .env.example .env
npm run dev
```

Never copy `backend/.env` into a submission archive. Rotate any key that was previously shared in an archive.

## Environment

Backend `.env`:

- `GEMINI_API_KEY`: backend-only Gemini credential.
- `GEMINI_MODEL`: supported Gemini model name.
- `FRONTEND_URL`: comma-separated allowed frontend origins.
- `REQUEST_TIMEOUT_SECONDS`: provider request timeout.

Frontend `.env`:

- `VITE_API_BASE_URL`: FastAPI base URL. Never put the Gemini key here.

## API

- `GET /health` - liveness check.
- `GET /api/status` - model/configured status without secrets.
- `POST /api/generate` - analyze a brief and generate ten tweets.
- `POST /api/regenerate/{tweet_id}` - generate one replacement.
- `POST /api/regenerate-all` - generate a fresh set of ten.

Provider errors are sanitized: invalid requests return 400, authentication/permission errors return 401/403, quota/rate limits return 429 without retrying exhausted quota, and transient provider failures return 502/504 after bounded retries.

## Testing

```powershell
cd backend
python -m pytest -q
cd ..\frontend
npm run build
```

All provider tests use mocked responses and do not consume Gemini quota. Live Gemini verification depends on provider availability and account quota. A daily free-tier quota exhaustion is an external 429 condition and cannot be fixed by retrying.

## Deployment

Deploy `backend` to Render with `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Deploy `frontend` to Vercel with `VITE_API_BASE_URL` set to the Render URL.

See [APPROACH.md](./APPROACH.md) for the implementation approach, [EXAMPLE_OUTPUTS.md](./EXAMPLE_OUTPUTS.md) for two illustrative brand outputs, and [DEPLOYMENT.md](./DEPLOYMENT.md) for the complete deployment checklist. No live URL is claimed until a deployment and health check have been completed.
