import time
import functools
from app.logger import get_logger

logger = get_logger("migru.performance")


def timing_decorator(func):
    """Decorator to measure function execution time."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} executed in {execution_time:.2f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.2f}s: {e}")
            raise

    return wrapper


def memory_usage_decorator(func):
    """Decorator to measure memory usage before and after function execution."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            import psutil

            process = psutil.Process()
            memory_before = process.memory_info().rss / 1024 / 1024  # MB

            result = func(*args, **kwargs)

            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_diff = memory_after - memory_before
            logger.info(
                f"{func.__name__} memory usage: {memory_before:.1f}MB -> {memory_after:.1f}MB ({memory_diff:+.1f}MB)"
            )
            return result
        except ImportError:
            # psutil not available, just run the function
            return func(*args, **kwargs)

    return wrapper


class PerformanceMonitor:
    """Simple performance monitoring for CLI operations."""

    def __init__(self):
        self.start_times = {}
        self.metrics = {}

    def start_timer(self, operation: str):
        """Start timing an operation."""
        self.start_times[operation] = time.time()
        logger.debug(f"Started timing: {operation}")

    def end_timer(self, operation: str):
        """End timing an operation and record the duration."""
        if operation in self.start_times:
            duration = time.time() - self.start_times[operation]
            if operation not in self.metrics:
                self.metrics[operation] = []
            self.metrics[operation].append(duration)
            logger.info(f"Operation '{operation}' completed in {duration:.2f}s")
            return duration
        return None

    def get_average_time(self, operation: str) -> float:
        """Get average execution time for an operation."""
        if operation in self.metrics and self.metrics[operation]:
            return sum(self.metrics[operation]) / len(self.metrics[operation])
        return 0.0

    def get_report(self) -> str:
        """Generate a performance report."""
        if not self.metrics:
            return "No performance metrics available."

        report = "Performance Report:\n"
        for operation, times in self.metrics.items():
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            report += f"  {operation}: avg={avg_time:.2f}s, min={min_time:.2f}s, max={max_time:.2f}s (runs={len(times)})\n"
        return report


# Global performance monitor instance
performance_monitor = PerformanceMonitor()
