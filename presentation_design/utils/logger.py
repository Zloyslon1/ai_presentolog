"""
Logging System Module
=====================

Structured JSON logging system with rotation, severity levels, and contextual fields.
Supports both file and console output with configurable formats.
"""

import json
import logging
import logging.handlers
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import traceback


class JSONFormatter(logging.Formatter):
    """
    Custom formatter that outputs log records as JSON.
    
    Includes timestamp, severity level, message, and contextual fields.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON string.
        
        Args:
            record: Log record to format
            
        Returns:
            JSON-formatted log string
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add exception information if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields from record
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'presentation_id'):
            log_data['presentation_id'] = record.presentation_id
        if hasattr(record, 'operation'):
            log_data['operation'] = record.operation
        if hasattr(record, 'duration'):
            log_data['duration_seconds'] = record.duration
        
        return json.dumps(log_data, ensure_ascii=False)


class PresentationLogger:
    """
    Centralized logger for the presentation design system.
    
    Provides structured logging with contextual information for tracking
    operations across the presentation processing pipeline.
    
    Attributes:
        logger (logging.Logger): Underlying Python logger
        context (Dict[str, Any]): Default context fields for all log entries
    """
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize logger with configuration.
        
        Args:
            name: Logger name (typically module name)
            config: Logging configuration dictionary with keys:
                - log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                - log_file_path: Path to log file or directory
                - log_format: Format type ('json' or 'text')
                - console_output: Whether to log to console (default: True)
                - retention_days: Days to keep log files (default: 30)
        """
        self.logger = logging.getLogger(name)
        self.context: Dict[str, Any] = {}
        
        # Default configuration
        if config is None:
            config = {
                'log_level': 'INFO',
                'log_file_path': 'logs',
                'log_format': 'json',
                'console_output': True,
                'retention_days': 30
            }
        
        self.config = config
        
        # Set log level
        level = getattr(logging, config.get('log_level', 'INFO').upper())
        self.logger.setLevel(level)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Add file handler with rotation
        self._setup_file_handler()
        
        # Add console handler if enabled
        if config.get('console_output', True):
            self._setup_console_handler()
    
    def _setup_file_handler(self) -> None:
        """
        Setup rotating file handler for logs.
        
        Creates daily log files with automatic rotation and retention.
        """
        log_path = Path(self.config['log_file_path'])
        
        # If path is a directory, create filename with date
        if log_path.is_dir() or not log_path.suffix:
            log_path = log_path / f"presentation_design.log"
        
        # Ensure directory exists
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create rotating file handler (daily rotation)
        file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=str(log_path),
            when='midnight',
            interval=1,
            backupCount=self.config.get('retention_days', 30),
            encoding='utf-8'
        )
        
        # Set format based on config
        if self.config.get('log_format', 'json') == 'json':
            file_handler.setFormatter(JSONFormatter())
        else:
            file_handler.setFormatter(
                logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            )
        
        self.logger.addHandler(file_handler)
    
    def _setup_console_handler(self) -> None:
        """
        Setup console handler for logs.
        
        Uses text format for better readability in console.
        """
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        )
        self.logger.addHandler(console_handler)
    
    def set_context(self, **kwargs: Any) -> None:
        """
        Set default context fields for all log entries from this logger.
        
        Args:
            **kwargs: Key-value pairs to include in all logs
            
        Example:
            >>> logger.set_context(request_id='abc123', user_id='user@example.com')
        """
        self.context.update(kwargs)
    
    def clear_context(self) -> None:
        """Clear all default context fields."""
        self.context.clear()
    
    def _log(self, level: int, message: str, **kwargs: Any) -> None:
        """
        Internal log method with context injection.
        
        Args:
            level: Log level constant from logging module
            message: Log message
            **kwargs: Additional context fields
        """
        # Merge default context with call-specific kwargs
        extra_data = {**self.context, **kwargs}
        
        # Create extra dict for logger
        extra = {}
        for key, value in extra_data.items():
            extra[key] = value
        
        self.logger.log(level, message, extra=extra)
    
    def debug(self, message: str, **kwargs: Any) -> None:
        """
        Log debug message.
        
        Args:
            message: Debug message
            **kwargs: Additional context fields
        """
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs: Any) -> None:
        """
        Log info message.
        
        Args:
            message: Info message
            **kwargs: Additional context fields
        """
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs: Any) -> None:
        """
        Log warning message.
        
        Args:
            message: Warning message
            **kwargs: Additional context fields
        """
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, exc_info: bool = False, **kwargs: Any) -> None:
        """
        Log error message.
        
        Args:
            message: Error message
            exc_info: Whether to include exception traceback
            **kwargs: Additional context fields
        """
        extra_data = {**self.context, **kwargs}
        extra = {}
        for key, value in extra_data.items():
            extra[key] = value
        
        self.logger.error(message, exc_info=exc_info, extra=extra)
    
    def critical(self, message: str, exc_info: bool = False, **kwargs: Any) -> None:
        """
        Log critical message.
        
        Args:
            message: Critical message
            exc_info: Whether to include exception traceback
            **kwargs: Additional context fields
        """
        extra_data = {**self.context, **kwargs}
        extra = {}
        for key, value in extra_data.items():
            extra[key] = value
        
        self.logger.critical(message, exc_info=exc_info, extra=extra)
    
    def log_operation(self, operation: str, status: str, **kwargs: Any) -> None:
        """
        Log an operation with standard fields.
        
        Args:
            operation: Operation name (e.g., "extract_content", "apply_design")
            status: Operation status (e.g., "started", "completed", "failed")
            **kwargs: Additional context fields
        """
        message = f"Operation {operation}: {status}"
        self.info(message, operation=operation, **kwargs)


# Global logger instances cache
_loggers: Dict[str, PresentationLogger] = {}


def get_logger(name: str, config: Optional[Dict[str, Any]] = None) -> PresentationLogger:
    """
    Get or create logger instance.
    
    Args:
        name: Logger name (typically __name__ from calling module)
        config: Optional logging configuration
        
    Returns:
        PresentationLogger instance
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing started", presentation_id="123")
    """
    if name not in _loggers:
        _loggers[name] = PresentationLogger(name, config)
    
    return _loggers[name]


def setup_logging_from_config(config_manager) -> None:
    """
    Setup logging system from configuration manager.
    
    Args:
        config_manager: Config instance with logging configuration
    """
    logging_config = config_manager.get_section('logging')
    
    # Update all existing loggers with new config
    for logger in _loggers.values():
        logger.config = logging_config
        logger.logger.handlers.clear()
        logger._setup_file_handler()
        if logging_config.get('console_output', True):
            logger._setup_console_handler()
