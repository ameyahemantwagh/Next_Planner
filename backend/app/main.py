from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import os
import asyncio
from .database import engine, Base
from . import models
from .auth import router as auth_router
from .planner_routes import router as planner_router
from .websockets import websocket_endpoint, redis_subscriber

app = FastAPI(title="Auth Prototype")

frontend_origins = [os.getenv("FRONTEND_URL", "http://localhost:9005")]

app.add_middleware(
    CORSMiddleware,
    # Allow only the configured frontend origin when credentials are included.
    allow_origins=frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(planner_router)

@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(redis_subscriber(loop))
    except Exception:
        pass

@app.get("/")
def root():
    return {"status": "ok"}


@app.websocket("/ws")
async def ws_route(websocket: WebSocket):
    await websocket_endpoint(websocket)


@app.middleware("http")
async def security_headers_middleware(request, call_next):
    response = await call_next(request)
    # HSTS - in production only
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "geolocation=()"
    # minimal CSP - tune for your app
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'"
    return response
