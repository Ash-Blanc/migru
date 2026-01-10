import json
import hashlib
from functools import wraps
from typing import Any, Optional
from app.db import db

class CacheService:
    def __init__(self, expiration: int = 3600):
        self.expiration = expiration  # Default 1 hour cache

    def generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generates a unique cache key based on arguments."""
        key_content = f"{prefix}:{args}:{kwargs}"
        return hashlib.sha256(key_content.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """Retrieves data from Redis."""
        try:
            data = db.redis.get(key)
            if data:
                return json.loads(data)
        except Exception:
            pass # Fail silently/gracefully
        return None

    def set(self, key: str, value: Any, expiration: int = None):
        """Sets data in Redis."""
        try:
            exp = expiration or self.expiration
            db.redis.setex(key, exp, json.dumps(value))
        except Exception:
            pass

    def cached(self, prefix: str, expiration: int = None):
        """Decorator for caching function results."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                key = self.generate_key(prefix, *args, **kwargs)
                cached_value = self.get(key)
                if cached_value:
                    return cached_value
                
                result = func(*args, **kwargs)
                self.set(key, result, expiration)
                return result
            return wrapper
        return decorator

cache_service = CacheService()
