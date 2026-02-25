"""
Rate limiter de finestra lliscant en memòria.
Thread-safe, sense dependències externes, per clau (user_id o IP).
"""
import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import HTTPException, status


class SlidingWindowLimiter:
    def __init__(self, max_calls: int, period_seconds: int):
        self._max    = max_calls
        self._period = period_seconds
        self._calls: dict[str, deque] = defaultdict(deque)
        self._lock   = Lock()

    def check(self, key: str) -> None:
        """Llança HTTP 429 si la clau ha superat el límit en el període actual."""
        now    = time.monotonic()
        cutoff = now - self._period
        with self._lock:
            dq = self._calls[key]
            while dq and dq[0] < cutoff:
                dq.popleft()
            if len(dq) >= self._max:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Massa peticions. Màxim {self._max} missatges per {self._period}s.",
                )
            dq.append(now)


# 10 missatges per minut per usuari — suficient per a una sessió de formació
chat_limiter = SlidingWindowLimiter(max_calls=10, period_seconds=60)
