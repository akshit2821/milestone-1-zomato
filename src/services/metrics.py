from __future__ import annotations


class MetricsCollector:
    def __init__(self) -> None:
        self.total_requests = 0
        self.success_requests = 0
        self.failed_requests = 0
        self.fallback_requests = 0
        self.total_latency_ms = 0
        self.last_latency_ms = 0
        self.latency_samples_ms: list[int] = []

    def record_success(self, latency_ms: int, fallback_used: bool) -> None:
        self.total_requests += 1
        self.success_requests += 1
        self.total_latency_ms += max(0, latency_ms)
        self.last_latency_ms = max(0, latency_ms)
        self.latency_samples_ms.append(self.last_latency_ms)
        if fallback_used:
            self.fallback_requests += 1

    def record_failure(self) -> None:
        self.total_requests += 1
        self.failed_requests += 1

    def snapshot(self) -> dict:
        avg_latency = (
            int(self.total_latency_ms / self.success_requests) if self.success_requests > 0 else 0
        )
        sorted_latencies = sorted(self.latency_samples_ms)
        p50 = self._percentile(sorted_latencies, 50)
        p95 = self._percentile(sorted_latencies, 95)
        return {
            "total_requests": self.total_requests,
            "success_requests": self.success_requests,
            "failed_requests": self.failed_requests,
            "fallback_requests": self.fallback_requests,
            "last_latency_ms": self.last_latency_ms,
            "avg_latency_ms": avg_latency,
            "p50_latency_ms": p50,
            "p95_latency_ms": p95,
        }

    @staticmethod
    def _percentile(sorted_values: list[int], percentile: int) -> int:
        if not sorted_values:
            return 0
        index = int(round((percentile / 100) * (len(sorted_values) - 1)))
        return sorted_values[index]
