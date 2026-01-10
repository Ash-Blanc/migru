from agno.db.redis import RedisDb
from app.config import config

def get_db():
    return RedisDb(db_url=config.REDIS_URL)

# Global db instance
db = get_db()
