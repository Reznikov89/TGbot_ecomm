"""
Metrics and monitoring module for TGecomm
"""
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
from .logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class Metric:
    """Single metric entry"""
    name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """Collects and stores application metrics"""
    
    def __init__(self) -> None:
        """Initialize metrics collector"""
        self.metrics: List[Metric] = []
        self.counters: Dict[str, int] = defaultdict(int)
        self.timers: Dict[str, List[float]] = defaultdict(list)
        self.errors: List[Dict[str, Any]] = []
        self.start_time = time.time()
    
    def increment(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None) -> None:
        """Increment a counter metric
        
        Args:
            name: Metric name
            value: Increment value (default: 1)
            tags: Optional tags for the metric
        """
        self.counters[name] += value
        self.metrics.append(Metric(
            name=name,
            value=float(value),
            tags=tags or {}
        ))
        logger.debug(f"Metric incremented: {name} = {self.counters[name]}")
    
    def record_timing(self, name: str, duration: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a timing metric
        
        Args:
            name: Metric name
            duration: Duration in seconds
            tags: Optional tags for the metric
        """
        self.timers[name].append(duration)
        self.metrics.append(Metric(
            name=f"{name}_duration",
            value=duration,
            tags=tags or {}
        ))
        logger.debug(f"Timing recorded: {name} = {duration:.3f}s")
    
    def record_error(self, error_type: str, error_message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Record an error
        
        Args:
            error_type: Type of error
            error_message: Error message
            context: Optional context information
        """
        self.errors.append({
            'type': error_type,
            'message': error_message,
            'timestamp': datetime.now(),
            'context': context or {}
        })
        self.increment('errors', tags={'type': error_type})
        logger.warning(f"Error recorded: {error_type} - {error_message}")
    
    def get_counter(self, name: str) -> int:
        """Get counter value
        
        Args:
            name: Counter name
            
        Returns:
            Counter value
        """
        return self.counters.get(name, 0)
    
    def get_timing_stats(self, name: str) -> Dict[str, float]:
        """Get timing statistics
        
        Args:
            name: Timer name
            
        Returns:
            Dictionary with min, max, avg, count
        """
        timings = self.timers.get(name, [])
        if not timings:
            return {'min': 0.0, 'max': 0.0, 'avg': 0.0, 'count': 0}
        
        return {
            'min': min(timings),
            'max': max(timings),
            'avg': sum(timings) / len(timings),
            'count': len(timings)
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary
        
        Returns:
            Dictionary with metrics summary
        """
        uptime = time.time() - self.start_time
        
        return {
            'uptime_seconds': uptime,
            'uptime_formatted': self._format_uptime(uptime),
            'counters': dict(self.counters),
            'timings': {
                name: self.get_timing_stats(name)
                for name in self.timers.keys()
            },
            'error_count': len(self.errors),
            'error_types': {
                error['type']: sum(1 for e in self.errors if e['type'] == error['type'])
                for error in self.errors
            },
            'total_metrics': len(self.metrics)
        }
    
    @staticmethod
    def _format_uptime(seconds: float) -> str:
        """Format uptime in human-readable format
        
        Args:
            seconds: Uptime in seconds
            
        Returns:
            Formatted uptime string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
    
    def reset(self) -> None:
        """Reset all metrics"""
        self.metrics.clear()
        self.counters.clear()
        self.timers.clear()
        self.errors.clear()
        self.start_time = time.time()
        logger.info("Metrics reset")


# Global metrics instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics() -> MetricsCollector:
    """Get global metrics collector instance
    
    Returns:
        MetricsCollector instance
    """
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def reset_metrics() -> None:
    """Reset global metrics"""
    global _metrics_collector
    if _metrics_collector:
        _metrics_collector.reset()


class TimingContext:
    """Context manager for timing operations"""
    
    def __init__(self, name: str, tags: Optional[Dict[str, str]] = None) -> None:
        """Initialize timing context
        
        Args:
            name: Metric name
            tags: Optional tags
        """
        self.name = name
        self.tags = tags
        self.start_time: Optional[float] = None
    
    def __enter__(self) -> 'TimingContext':
        """Start timing"""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """End timing and record metric"""
        if self.start_time:
            duration = time.time() - self.start_time
            get_metrics().record_timing(self.name, duration, self.tags)

