import time
import logging
from typing import Callable, Any
from app.logger import get_logger

logger = get_logger("migru.monitor")

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            "total_requests": 0,
            "total_latency": 0,
            "errors": 0
        }

    def track_latency(self, func: Callable) -> Callable:
        """Decorator to track execution time."""
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                latency = time.time() - start_time
                self._record_success(latency)
                return result
            except Exception as e:
                self._record_error()
                logger.error(f"Execution failed in {func.__name__}: {e}")
                raise e
        return wrapper

    def _record_success(self, latency: float):
        self.metrics["total_requests"] += 1
        self.metrics["total_latency"] += latency

    def _record_error(self):
        self.metrics["errors"] += 1

    def get_stats(self):
        avg_latency = 0
        if self.metrics["total_requests"] > 0:
            avg_latency = self.metrics["total_latency"] / self.metrics["total_requests"]
        
        return {
            "requests": self.metrics["total_requests"],
            "avg_latency_sec": round(avg_latency, 4),
            "errors": self.metrics["errors"]
        }

monitor = PerformanceMonitor()
