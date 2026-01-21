from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from . import models
from .auth import router as auth_router

app = FastAPI(title="Auth Prototype")

app.add_middleware(
    CORSMiddleware,
    # In development allow the frontend dev server and other local origins.
    # Use a permissive setting here so the containerized frontend can reach the API.
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"status": "ok"}


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
