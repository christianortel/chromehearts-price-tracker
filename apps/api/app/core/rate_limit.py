from collections import defaultdict, deque
from time import time

from fastapi import HTTPException, Request, status


class InMemoryRateLimiter:
    def __init__(self, limit: int, window_seconds: int) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._requests: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str) -> None:
        now = time()
        entries = self._requests[key]
        while entries and now - entries[0] > self.window_seconds:
            entries.popleft()
        if len(entries) >= self.limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later.",
            )
        entries.append(now)


submission_rate_limiter = InMemoryRateLimiter(limit=10, window_seconds=3600)


def limit_submissions(request: Request) -> None:
    forwarded_for = request.headers.get("x-forwarded-for")
    client_key = forwarded_for or (request.client.host if request.client else "unknown")
    submission_rate_limiter.check(client_key)
