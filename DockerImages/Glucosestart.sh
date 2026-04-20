#!/bin/bash
echo "Spouštím aplikaci..."
# start nginx
nginx
# Můžeš provést migrace nebo jiné úkoly:
alembic upgrade head

# Spuštění FastAPI (uvicorn)
uvicorn glucose_viewer.main:app --app-dir src --host 127.0.0.1 --port 8087
echo "Uvicorn glucose-api is running on port 8087"