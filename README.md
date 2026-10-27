# HR Policy Assistant

Answers employee questions using only the XYZ Company Leave Policy (`data/`),
cites the policy section, says "I don't know, please contact HR." when the
policy is silent, and refuses requests for other employees' personal data.

## Run it
Requires Python 3.10+, a free [Groq](https://console.groq.com) API key and a
free [Qdrant Cloud](https://cloud.qdrant.io) cluster (URL + API key).

```bash
pip install -e . && pip install -r backend/requirements.txt -r frontend/requirements.txt
cp .env.example .env            # then add your own keys
python -m backend.scripts.ingest_policy   # index the policy (run once)
uvicorn backend.app.main:app --port 8000  # terminal 1: API
streamlit run frontend/app.py             # terminal 2: UI -> http://localhost:8501
```

Set `BACKEND_API_URL` if the API is not at `http://127.0.0.1:8000/api`.
Tests: `pytest tests`.

## Deploy
**Backend (Render):** Python 3.12 (`PYTHON_VERSION=3.12`), health check `/api/health`.
- Build: `pip install -e . && pip install -r backend/requirements.txt && python -c "from backend.app.infrastructure.embeddings import get_embedding_model as g; g()"`
- Start: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
- Env vars: those in `.env.example`, with `CORS_ORIGINS` set to your frontend URL.

**Frontend (Streamlit Cloud):** add the secret `BACKEND_API_URL = "https://<your-service>.onrender.com/api"`.

Free Render instances sleep after ~15 minutes; the first question after a pause can take up to a minute.
