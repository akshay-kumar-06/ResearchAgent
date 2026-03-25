"""
Metrics collection and monitoring for the Multi-Agent Research Assistant
"""

import time
import structlog
from typing import Dict, Any, Optional
from datetime import datetime
from contextlib import contextmanager

logger = structlog.get_logger()


class MetricsCollector:
    """Collects and stores metrics for research operations"""

    def __init__(self):
        self.metrics: Dict[str, Any] = {
            "research_count": 0,
            "successful_research": 0,
            "failed_research": 0,
            "total_execution_time": 0.0,
            "average_execution_time": 0.0,
            "sources_per_research": [],
            "accuracy_scores": [],
            "uptime_start": time.time(),
        }

    def increment_research_count(self):
        """Increment total research count"""
        self.metrics["research_count"] += 1

    def increment_successful_research(self):
        """Increment successful research count"""
        self.metrics["successful_research"] += 1

    def increment_failed_research(self):
        """Increment failed research count"""
        self.metrics["failed_research"] += 1

    def record_execution_time(self, execution_time: float):
        """Record execution time for a research operation"""
        self.metrics["total_execution_time"] += execution_time
        if self.metrics["research_count"] > 0:
            self.metrics["average_execution_time"] = (
                self.metrics["total_execution_time"] / self.metrics["research_count"]
            )

    def record_sources_count(self, sources_count: int):
        """Record number of sources found in research"""
        self.metrics["sources_per_research"].append(sources_count)
        # Keep only last 100 entries to prevent memory growth
        if len(self.metrics["sources_per_research"]) > 100:
            self.metrics["sources_per_research"] = self.metrics["sources_per_research"][
                -100:
            ]

    def record_accuracy_score(self, score: float):
        """Record accuracy score (0.0 to 1.0) for research"""
        self.metrics["accuracy_scores"].append(score)
        # Keep only last 100 entries
        if len(self.metrics["accuracy_scores"]) > 100:
            self.metrics["accuracy_scores"] = self.metrics["accuracy_scores"][-100:]

    def get_uptime(self) -> float:
        """Get application uptime in seconds"""
        return time.time() - self.metrics["uptime_start"]

    def get_average_sources(self) -> float:
        """Get average number of sources per research"""
        if not self.metrics["sources_per_research"]:
            return 0.0
        return sum(self.metrics["sources_per_research"]) / len(
            self.metrics["sources_per_research"]
        )

    def get_average_accuracy(self) -> float:
        """Get average accuracy score"""
        if not self.metrics["accuracy_scores"]:
            return 0.0
        return sum(self.metrics["accuracy_scores"]) / len(
            self.metrics["accuracy_scores"]
        )

    def get_success_rate(self) -> float:
        """Get success rate as percentage"""
        total = self.metrics["successful_research"] + self.metrics["failed_research"]
        if total == 0:
            return 0.0
        return (self.metrics["successful_research"] / total) * 100

    def get_metrics(self) -> Dict[str, Any]:
        """Get all current metrics"""
        return {
            **self.metrics,
            "uptime_seconds": self.get_uptime(),
            "average_sources": self.get_average_sources(),
            "average_accuracy": self.get_average_accuracy(),
            "success_rate": self.get_success_rate(),
        }


# Global metrics collector instance
metrics_collector = MetricsCollector()


@contextmanager
def time_operation(operation_name: str):
    """Context manager to time an operation"""
    start_time = time.time()
    try:
        yield
    finally:
        execution_time = time.time() - start_time
        logger.info(f"{operation_name}_completed", execution_time=execution_time)


def record_research_metrics(
    status: str,
    execution_time: float,
    sources_count: int = 0,
    accuracy_score: Optional[float] = None,
):
    """Record metrics for a completed research operation"""
    metrics_collector.increment_research_count()

    if status == "complete":
        metrics_collector.increment_successful_research()
    else:
        metrics_collector.increment_failed_research()

    metrics_collector.record_execution_time(execution_time)
    metrics_collector.record_sources_count(sources_count)

    if accuracy_score is not None:
        metrics_collector.record_accuracy_score(accuracy_score)

    logger.info(
        "research_metrics_recorded",
        status=status,
        execution_time=execution_time,
        sources_count=sources_count,
        accuracy_score=accuracy_score,
    )
