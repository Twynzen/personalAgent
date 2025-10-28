"""
Structured logging for Sendell.

Features:
- JSON structured logging
- PII scrubbing (emails, phones, credit cards)
- Rotating file handler
- Console output with colors (via rich)
"""

import logging
import re
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict

from rich.console import Console
from rich.logging import RichHandler

from sendell.config import get_settings


# PII patterns to scrub from logs
PII_PATTERNS = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    "phone": re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"),
}


def scrub_pii(text: str) -> str:
    """
    Remove PII from text.

    Args:
        text: Text to scrub

    Returns:
        Scrubbed text with PII replaced by [REDACTED]
    """
    settings = get_settings()
    if not settings.agent.scrub_pii:
        return text

    for pattern_name, pattern in PII_PATTERNS.items():
        text = pattern.sub(f"[REDACTED_{pattern_name.upper()}]", text)

    return text


class PIIFilter(logging.Filter):
    """Filter to scrub PII from log records"""

    def filter(self, record: logging.LogRecord) -> bool:
        """Scrub PII from message and args"""
        if hasattr(record, "msg") and isinstance(record.msg, str):
            record.msg = scrub_pii(record.msg)

        if hasattr(record, "args") and record.args:
            if isinstance(record.args, dict):
                record.args = {k: scrub_pii(str(v)) for k, v in record.args.items()}
            elif isinstance(record.args, tuple):
                record.args = tuple(scrub_pii(str(arg)) for arg in record.args)

        return True


def setup_logger(name: str = "sendell") -> logging.Logger:
    """
    Setup structured logger with file and console handlers.

    Args:
        name: Logger name

    Returns:
        Configured logger instance
    """
    settings = get_settings()

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(settings.logging.level.value)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Console handler with Rich
    console = Console()
    console_handler = RichHandler(
        console=console,
        rich_tracebacks=True,
        tracebacks_show_locals=settings.advanced.debug,
        show_time=True,
        show_path=settings.advanced.debug,
    )
    console_handler.setLevel(settings.logging.level.value)

    # File handler with rotation
    settings.logging.file.parent.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        settings.logging.file,
        maxBytes=settings.logging.max_size * 1024 * 1024,  # MB to bytes
        backupCount=settings.logging.backup_count,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)  # Log everything to file

    # Formatting
    console_format = "%(message)s"
    file_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"

    console_handler.setFormatter(logging.Formatter(console_format))
    file_handler.setFormatter(logging.Formatter(file_format))

    # Add PII filter if enabled
    if settings.agent.scrub_pii:
        pii_filter = PIIFilter()
        console_handler.addFilter(pii_filter)
        file_handler.addFilter(pii_filter)

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


def log_function_call(logger: logging.Logger, func_name: str, **kwargs: Any) -> None:
    """
    Log a function call with structured data.

    Args:
        logger: Logger instance
        func_name: Function name
        **kwargs: Function arguments to log
    """
    args_str = ", ".join(f"{k}={v}" for k, v in kwargs.items())
    logger.debug(f"Calling {func_name}({args_str})")


def log_tool_execution(
    logger: logging.Logger, tool_name: str, params: Dict[str, Any], result: Any = None
) -> None:
    """
    Log MCP tool execution.

    Args:
        logger: Logger instance
        tool_name: Tool name
        params: Tool parameters
        result: Tool result (optional)
    """
    logger.info(f"Executing tool: {tool_name}", extra={"tool": tool_name, "params": params})
    if result is not None:
        logger.debug(f"Tool result: {result}", extra={"tool": tool_name, "result": result})


# Global logger instance
_logger = None


def get_logger(name: str = "sendell") -> logging.Logger:
    """
    Get or create the global logger instance.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    global _logger
    if _logger is None:
        _logger = setup_logger(name)
    return _logger
