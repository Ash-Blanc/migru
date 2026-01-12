import subprocess
import time

from agno.db.redis import RedisDb

from app.config import config
from app.logger import get_logger

logger = get_logger("migru.db")

def ensure_redis_running() -> bool:
    """Checks if redis-server is running and attempts to start it if not."""
    from redis import Redis
    
    def check_connection():
        try:
            client = Redis.from_url(config.REDIS_URL)
            return client.ping()
        except Exception:
            return False

    if check_connection():
        return True

    # Downgraded to debug to reduce CLI noise
    logger.debug("Redis is not running. Attempting to start redis-server...")
    try:
        # Attempt to start redis-server in the background
        subprocess.Popen(
            ["redis-server"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Wait up to 5 seconds for it to become available
        for _ in range(10):
            time.sleep(0.5)
            if check_connection():
                logger.debug("Redis server started successfully.")
                return True
                
        logger.debug("Redis server started but failed to respond to ping.")
        return False
    except FileNotFoundError:
        logger.debug("redis-server executable not found in PATH.")
        return False
    except Exception as e:
        logger.debug(f"Could not start redis-server: {e}")
        return False

def get_db() -> RedisDb:
    return RedisDb(db_url=config.REDIS_URL)

# Global db instance
db = get_db()
