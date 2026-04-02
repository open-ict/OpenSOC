from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import HTTPException, Request
from app.core.config import settings

_hits = defaultdict(list)


def tenant_rate_limit(request: Request, tenant_key: str):
    now = datetime.utcnow()
    bucket = _hits[tenant_key]
    window_start = now - timedelta(minutes=1)
    while bucket and bucket[0] < window_start:
        bucket.pop(0)
    if len(bucket) >= settings.DEFAULT_RATE_LIMIT_PER_MINUTE:
        raise HTTPException(status_code=429, detail='Rate limit exceeded for tenant')
    bucket.append(now)
