# Dart Game Pro v3.1 Server Deployment

**Production-ready FastAPI backend for real-time multiplayer (ELO, custom modes, history, Redis-ready). Works seamlessly with the Streamlit Online tab.**

## Run locally
```bash
pip install -r requirements.txt
# Terminal 1: Streamlit
python main.py

# Terminal 2: FastAPI multiplayer server
uvicorn core.server.main:app --host 0.0.0.0 --port 8001 --reload
```

## Docker (recommended)
See docker-compose.yml (create one):
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8501:8501"
    depends_on:
      - server
  server:
    build: .
    command: uvicorn core.server.main:app --host 0.0.0.0 --port 8001
    ports:
      - "8001:8001"
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
  redis:
    image: redis:alpine
```

## Production
- Use gunicorn + uvicorn workers for server.
- Redis for pub/sub and rate limits.
- JWT secret from env.
- Add rate limiting middleware, auth DB.
- Deploy server to Fly.io / Railway / Render; Streamlit to Streamlit Cloud or same.

See GitHub issues for full P0-1 implementation.
```

To use: run the two commands, go to Online tab in app, connect using match_id from /matches POST (use curl or the /docs).

This starts the real-time backend.
