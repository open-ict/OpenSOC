import json
import redis
from app.core.config import settings

QUEUE_MAIN = 'opensoc:jobs'
QUEUE_DLQ = 'opensoc:jobs:dead'
QUEUE_SYNC = 'opensoc:jobs:sync'


def get_redis():
    return redis.from_url(settings.REDIS_URL)


def enqueue(queue_name: str, payload: dict):
    r = get_redis()
    r.rpush(queue_name, json.dumps(payload))


def list_dead_letter(limit: int = 100):
    r = get_redis()
    items = r.lrange(QUEUE_DLQ, 0, max(limit - 1, 0))
    return [json.loads(x) for x in items]
