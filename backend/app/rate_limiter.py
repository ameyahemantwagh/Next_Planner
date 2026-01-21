import os
import time
from collections import deque, defaultdict

REDIS_URL = os.getenv("REDIS_URL")

redis_client = None
if REDIS_URL:
    try:
        from redis import Redis
        from urllib.parse import urlparse

        redis_client = Redis.from_url(REDIS_URL)
        # test connection
        redis_client.ping()
    except Exception as e:
        print(f"[WARN] Redis unavailable: {e}")
        redis_client = None


class InMemoryLimiter:
    def __init__(self, calls: int, per_seconds: int):
        self.calls = calls
        self.per = per_seconds
        self.data = defaultdict(lambda: deque())

    def allow(self, key: str) -> bool:
        now = time.time()
        dq = self.data[key]
        while dq and dq[0] <= now - self.per:
            dq.popleft()
        if len(dq) < self.calls:
            dq.append(now)
            return True
        return False


class RedisLimiter:
    def __init__(self, calls: int, per_seconds: int):
        self.calls = calls
        self.per = per_seconds

    def allow(self, key: str) -> bool:
        if not redis_client:
            return True
        k = f"rl:{key}"
        try:
            current = redis_client.incr(k)
            if current == 1:
                redis_client.expire(k, self.per)
            return current <= self.calls
        except Exception:
            # if Redis fails, be permissive (fail open) but log
            print("[WARN] Redis rate limiter failed, allowing request")
            return True


# choose backend limiter
if redis_client:
    ip_limiter = RedisLimiter(100, 60)
    auth_limiter = RedisLimiter(10, 60)
else:
    ip_limiter = InMemoryLimiter(100, 60)
    auth_limiter = InMemoryLimiter(10, 60)


def check_ip(request) -> bool:
    ip = request.client.host if request and request.client else 'unknown'
    return ip_limiter.allow(ip)


def check_key(key: str) -> bool:
    return auth_limiter.allow(key)
