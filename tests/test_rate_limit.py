import pytest
from fastapi import HTTPException

from app.core.rate_limit import SlidingWindowLimiter


class TestSlidingWindowLimiter:
    def test_allows_within_limit(self):
        limiter = SlidingWindowLimiter(max_calls=3, period_seconds=60)
        for _ in range(3):
            limiter.check("user1")  # should not raise

    def test_blocks_over_limit(self):
        limiter = SlidingWindowLimiter(max_calls=2, period_seconds=60)
        limiter.check("user1")
        limiter.check("user1")
        with pytest.raises(HTTPException) as exc_info:
            limiter.check("user1")
        assert exc_info.value.status_code == 429

    def test_different_keys_independent(self):
        limiter = SlidingWindowLimiter(max_calls=1, period_seconds=60)
        limiter.check("user1")
        limiter.check("user2")  # different key, should not raise

    def test_window_expires(self):
        import time
        limiter = SlidingWindowLimiter(max_calls=1, period_seconds=0.1)  # 100ms window
        limiter.check("user1")
        with pytest.raises(HTTPException):
            limiter.check("user1")
        time.sleep(0.15)  # wait for window to expire
        limiter.check("user1")  # should work again

    def test_429_detail_message(self):
        limiter = SlidingWindowLimiter(max_calls=1, period_seconds=60)
        limiter.check("x")
        with pytest.raises(HTTPException) as exc_info:
            limiter.check("x")
        assert "Massa peticions" in exc_info.value.detail
