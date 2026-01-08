"""
Centralized logging for the entire application with color support.
Logs to console AND optional file for production debugging.
"""
import logging
import sys
from pathlib import Path
from datetime import datetime

# Color codes for terminal output
COLORS = {
    "DEBUG": "\033[36m",      # Cyan
    "INFO": "\033[32m",       # Green
    "WARNING": "\033[33m",    # Yellow
    "ERROR": "\033[31m",      # Red
    "CRITICAL": "\033[35m",   # Magenta
    "RESET": "\033[0m",       # Reset
}


class ColorFormatter(logging.Formatter):
    """Custom formatter with color support for terminal output"""
    
    def format(self, record):
        if sys.stdout.isatty():
            levelname = record.levelname
            color = COLORS.get(levelname, COLORS["RESET"])
            record.levelname = f"{color}{levelname}{COLORS['RESET']}"
        
        return super().format(record)


# Create logs directory
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


def setup_logger(
    name: str = __name__,
    level: str = "INFO",
    log_file: str | None = None
) -> logging.Logger:
    """
    Configure logger with console and optional file handlers.
    
    Args:
        name: Logger name (usually __name__)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Console handler - always active with color
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    console_format = ColorFormatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler - if log file path provided
    if log_file:
        try:
            log_path = Path(log_file) if not Path(log_file).is_absolute() else Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_path, mode='a')
            file_handler.setLevel(logging.DEBUG)  # File captures everything
            
            file_format = logging.Formatter(
                "%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            file_handler.setFormatter(file_format)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Failed to setup file logging: {e}")
    
    return logger


def log_startup_info(logger: logging.Logger, config: dict):
    """Log startup information for debugging"""
    logger.info("=" * 80)
    logger.info("CAMPUSSHIELD AI - STARTUP")
    logger.info("=" * 80)
    
    for key, value in config.items():
        # Don't log sensitive data
        if "key" in key.lower() or "password" in key.lower() or "secret" in key.lower():
            value = "***REDACTED***"
        logger.info(f"{key}: {value}")
    
    logger.info("=" * 80)


def log_request(logger: logging.Logger, method: str, path: str, status: int, latency_ms: float):
    """Log incoming request with latency"""
    logger.info(f"{method:6s} {path:40s} -> {status} [{latency_ms:.2f}ms]")


def log_error(logger: logging.Logger, error_type: str, message: str, exc_info=None):
    """Log error with optional exception info"""
    logger.error(f"{error_type}: {message}", exc_info=exc_info)


# Default logger instance
logger = setup_logger()

