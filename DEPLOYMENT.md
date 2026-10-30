# Deployment Instructions

## Backend on Render

1. Create a Render Web Service from this project.
2. Set the root directory to `backend`.
3. Set the runtime to Python.
4. Build command:

   ```text
   pip install -r requirements.txt
   ```

5. Start command:

   ```text
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

6. Configure these Render environment variables:
   - `GEMINI_API_KEY`: add through Render's secret environment-variable UI.
   - `GEMINI_MODEL`: a model enabled for the account.
   - `FRONTEND_URL`: the deployed Vercel origin.
   - `REQUEST_TIMEOUT_SECONDS`: `45`.
7. Verify `https://<render-service>/health` returns `{"status":"ok"}`.

## Frontend on Vercel

1. Create a Vercel project from this repository.
2. Set the root directory to `frontend`.
3. Build command:

   ```text
   npm run build
   ```

4. Set the output directory to `dist`.
5. Configure `VITE_API_BASE_URL` to the deployed Render backend URL.
6. Deploy and verify the form, loading state, generation error handling, copy, edit, and regeneration flows.

## Local production checks

```powershell
cd backend
python -m pytest -q
cd ..\frontend
npm install
npm run build
```

No live deployment URL is provided until a deployment has completed and the health endpoint and frontend have been verified. The current project has not been deployed from this workspace.
