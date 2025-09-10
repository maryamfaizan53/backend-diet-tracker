# py
import time
import asyncio
from typing import Dict
from app.core.config import get_settings

settings = get_settings()

class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last = time.monotonic()
        self.lock = asyncio.Lock()

    async def consume(self, amount: int = 1) -> bool:
        async with self.lock:
            now = time.monotonic()
            elapsed = now - self.last
            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
            self.last = now
            if self.tokens >= amount:
                self.tokens -= amount
                return True
            return False

_bucket_store: Dict[str, TokenBucket] = {}

def get_bucket(key: str) -> TokenBucket:
    if key not in _bucket_store:
        _bucket_store[key] = TokenBucket(settings.RATE_LIMIT_TOKENS, settings.RATE_LIMIT_RATE)
    return _bucket_store[key]

async def allow_request(key: str) -> bool:
    bucket = get_bucket(key)
    return await bucket.consume(1)
