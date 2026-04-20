from fastapi import FastAPI, Request
from glucose_viewer.api import relationCP
from glucose_viewer.exceptions.exceptions  import GlucoseAPIException
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import time
import asyncio
import os,logging, traceback

from glucose_viewer.api import GlukoseAPI, WebSocket, appUsers, clients, measurements, patients
API_VERSION = "1.1.0"
API_PASSWORD = os.getenv("API_PASSWORD", "change-me")
REACT_HOST = os.getenv("REACT_HOST", "localhost")
REACT_PORT = os.getenv("REACT_PORT", "5173")
if not REACT_HOST:
    raise RuntimeError("Environment variable REACT_HOST must be set.")
log = logging.getLogger("viewer")
def include_routers(app) -> FastAPI:
    app.include_router(GlukoseAPI.router)
    app.include_router(WebSocket.router)
    app.include_router(clients.router)
    app.include_router(patients.router)
    app.include_router(measurements.router)
    app.include_router(relationCP.router)
    app.include_router(appUsers.router)



app = FastAPI(title="Glucose viewer API", version=API_VERSION, docs_url="/docs", openapi_url="/openapi.json", root_path=os.getenv("VITE_GLUCOSE_ROOT_PATH", ""))

# Registr Prometheus metrcs
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"http://{REACT_HOST}:{REACT_PORT}"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

EXCLUDED_PATHS = {
    "/docs",
    "/openapi.json",
    "/redoc",
    "/favicon.ico",
}
RATE_LIMIT = 5
WINDOW_SECONDS = 1.0

request_times = []
lock = asyncio.Lock()
@app.middleware("http")
async def rate_limit(request: Request, call_next):
    if request.url.path in EXCLUDED_PATHS:
        return await call_next(request)

    async with lock:
        now = time.time()

        # odstranit staré requesty mimo časové okno
        while request_times and request_times[0] <= now - WINDOW_SECONDS:
            request_times.pop(0)

        if len(request_times) >= RATE_LIMIT:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too Many Requests"},
            )

        request_times.append(now)

    return await call_next(request)

@app.middleware("http")
async def global_exception_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except GlucoseAPIException as exc:
        log.error(f"Error: {str(exc)}, traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=400,
            content={"code": "invalid_input",
                     "data":{"message":str(exc.__class__),"message_datails": f"Service provisioning error: {str(exc)}"},
                     "status": "error",
                     "status_code":400
                     }
        )
    except Exception as exc:
        log.error(f"Error: {str(exc)}, traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={"code": "invalid_input",
                     "data":{"message":str(exc.__class__),"message_datails": f"Service provisioning error: {str(exc)}"},
                     "status": "error",
                     "status_code":500
                     }
        )
include_routers(app)