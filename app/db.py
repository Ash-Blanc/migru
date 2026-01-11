import subprocess
import time

from agno.db.redis import RedisDb

from app.config import config
from app.logger import get_logger

logger = get_logger("migru.db")

def ensure_redis_running() -> bool:
    """Checks if redis-server is running and attempts to start it if not."""
    try:
        # Check if we can connect to redis client
        from redis import Redis
        client = Redis.from_url(config.REDIS_URL)
        if client.ping():
            return True
    except Exception:
        logger.warning("Redis is not running. Attempting to start redis-server...")
        try:
            # Attempt to start redis-server in the background
            subprocess.Popen(
                ["redis-server"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            # Give it a few seconds to start
            time.sleep(2)
            return True
        except Exception as e:
            logger.error(f"Could not start redis-server: {e}")
            return False
    return False

def get_db() -> RedisDb:
    return RedisDb(db_url=config.REDIS_URL)

# Global db instance
db = get_db()
