"""
TGecomm - Telegram Client Application
"""
__version__ = "1.0.0"

from .client import TGecommClient
from .config import Config
from .ui import ConsoleUI
from .logger import setup_logger
from .metrics import get_metrics, MetricsCollector, TimingContext

__all__ = [
    'TGecommClient',
    'Config',
    'ConsoleUI',
    'setup_logger',
    'get_metrics',
    'MetricsCollector',
    'TimingContext',
]

