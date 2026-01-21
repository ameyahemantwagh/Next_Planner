import sys
import os
from fastapi.testclient import TestClient

# ensure project root on sys.path for imports when running under pytest in container
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import main as app_main
from app import rate_limiter
from app.database import Base, engine


# ensure DB tables exist for tests (uses default sqlite dev.db)
Base.metadata.create_all(bind=engine)


def test_rate_limit_signup():
    client = TestClient(app_main.app)
    # Use in-memory limiter with low threshold for test
    rate_limiter.ip_limiter = rate_limiter.InMemoryLimiter(2, 60)
    # first two requests allowed
    r1 = client.post("/api/auth/signup", json={"email": "rl1@example.com", "password": "testpassword123"})
    assert r1.status_code == 200
    r2 = client.post("/api/auth/signup", json={"email": "rl2@example.com", "password": "testpassword123"})
    assert r2.status_code == 200
    # third should be rate-limited
    r3 = client.post("/api/auth/signup", json={"email": "rl3@example.com", "password": "testpassword123"})
    assert r3.status_code == 429


def test_csrf_protection_logout_and_refresh():
    client = TestClient(app_main.app)
    # logout without CSRF header should be forbidden
    r = client.post("/api/auth/logout")
    assert r.status_code == 403

    # refresh without CSRF header should be forbidden
    r2 = client.post("/api/auth/refresh")
    assert r2.status_code == 403
