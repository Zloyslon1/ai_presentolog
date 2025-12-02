"""
Retry Logic Module
==================

Decorator and utilities for implementing retry logic with exponential backoff.
Handles transient failures in API calls and network operations.
"""

import time
import functools
from typing import Callable, Tuple, Type, Optional, Any
from .logger import get_logger

logger = get_logger(__name__)


class RetryError(Exception):
    """Raised when retry attempts are exhausted."""
    pass


def exponential_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None
) -> Callable:
    """
    Decorator for retrying functions with exponential backoff.
    
    Retries the decorated function on specified exceptions, waiting progressively
    longer between each attempt using exponential backoff algorithm.
    
    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay in seconds before first retry (default: 1.0)
        backoff_factor: Multiplier for delay after each retry (default: 2.0)
        exceptions: Tuple of exception types to catch and retry
        on_retry: Optional callback function called on each retry with (exception, attempt_number)
        
    Returns:
        Decorated function with retry logic
        
    Raises:
        RetryError: When max retries exhausted, wrapping the last exception
        
    Example:
        >>> @exponential_backoff(max_retries=3, exceptions=(ConnectionError,))
        ... def fetch_data(url):
        ...     return requests.get(url)
        
        >>> # First failure: wait 1 second
        >>> # Second failure: wait 2 seconds
        >>> # Third failure: wait 4 seconds
        >>> # Fourth failure: raise RetryError
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempt = 0
            delay = initial_delay
            last_exception = None
            
            while attempt <= max_retries:
                try:
                    # Attempt function call
                    result = func(*args, **kwargs)
                    
                    # Log success if this was a retry
                    if attempt > 0:
                        logger.info(
                            f"Function {func.__name__} succeeded after {attempt} retries",
                            operation=func.__name__,
                            retry_attempt=attempt
                        )
                    
                    return result
                    
                except exceptions as e:
                    last_exception = e
                    attempt += 1
                    
                    # If max retries reached, raise RetryError
                    if attempt > max_retries:
                        logger.error(
                            f"Function {func.__name__} failed after {max_retries} retries",
                            operation=func.__name__,
                            max_retries=max_retries,
                            exc_info=True
                        )
                        raise RetryError(
                            f"Max retries ({max_retries}) exceeded for {func.__name__}"
                        ) from e
                    
                    # Log retry attempt
                    logger.warning(
                        f"Function {func.__name__} failed (attempt {attempt}/{max_retries}), "
                        f"retrying in {delay:.1f} seconds: {str(e)}",
                        operation=func.__name__,
                        retry_attempt=attempt,
                        delay=delay,
                        exception_type=type(e).__name__
                    )
                    
                    # Call retry callback if provided
                    if on_retry:
                        on_retry(e, attempt)
                    
                    # Wait before retry
                    time.sleep(delay)
                    
                    # Increase delay exponentially
                    delay *= backoff_factor
            
            # Should not reach here, but raise last exception if it happens
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator


def retry_on_condition(
    condition: Callable[[Exception], bool],
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0
) -> Callable:
    """
    Decorator for retrying based on custom condition.
    
    Similar to exponential_backoff, but uses a custom condition function
    to determine whether to retry based on the exception.
    
    Args:
        condition: Function that takes exception and returns True to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for delay
        
    Returns:
        Decorated function with conditional retry logic
        
    Example:
        >>> def should_retry(exc):
        ...     return isinstance(exc, APIError) and exc.status_code == 429
        >>> 
        >>> @retry_on_condition(should_retry, max_retries=5)
        ... def call_api():
        ...     pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempt = 0
            delay = initial_delay
            
            while attempt <= max_retries:
                try:
                    result = func(*args, **kwargs)
                    
                    if attempt > 0:
                        logger.info(
                            f"Function {func.__name__} succeeded after {attempt} retries",
                            operation=func.__name__,
                            retry_attempt=attempt
                        )
                    
                    return result
                    
                except Exception as e:
                    # Check if we should retry based on condition
                    if not condition(e):
                        # Don't retry, re-raise immediately
                        logger.error(
                            f"Function {func.__name__} failed with non-retryable error",
                            operation=func.__name__,
                            exception_type=type(e).__name__,
                            exc_info=True
                        )
                        raise
                    
                    attempt += 1
                    
                    if attempt > max_retries:
                        logger.error(
                            f"Function {func.__name__} failed after {max_retries} retries",
                            operation=func.__name__,
                            max_retries=max_retries,
                            exc_info=True
                        )
                        raise RetryError(
                            f"Max retries ({max_retries}) exceeded for {func.__name__}"
                        ) from e
                    
                    logger.warning(
                        f"Function {func.__name__} failed (attempt {attempt}/{max_retries}), "
                        f"retrying in {delay:.1f} seconds",
                        operation=func.__name__,
                        retry_attempt=attempt,
                        delay=delay
                    )
                    
                    time.sleep(delay)
                    delay *= backoff_factor
        
        return wrapper
    return decorator


def is_rate_limit_error(exception: Exception) -> bool:
    """
    Check if exception is a rate limit error.
    
    Detects HTTP 429 (Too Many Requests) errors from various libraries.
    
    Args:
        exception: Exception to check
        
    Returns:
        True if rate limit error, False otherwise
    """
    # Check for googleapiclient errors
    if hasattr(exception, 'resp') and hasattr(exception.resp, 'status'):
        return exception.resp.status == 429
    
    # Check for requests library errors
    if hasattr(exception, 'response') and hasattr(exception.response, 'status_code'):
        return exception.response.status_code == 429
    
    # Check error message
    error_msg = str(exception).lower()
    return 'rate limit' in error_msg or 'quota exceeded' in error_msg or '429' in error_msg


def is_transient_error(exception: Exception) -> bool:
    """
    Check if exception is a transient error that should be retried.
    
    Detects network errors, timeouts, and temporary server errors.
    
    Args:
        exception: Exception to check
        
    Returns:
        True if transient error, False otherwise
    """
    # Check for rate limit errors
    if is_rate_limit_error(exception):
        return True
    
    # Check for HTTP 5xx errors (server errors)
    if hasattr(exception, 'resp') and hasattr(exception.resp, 'status'):
        status = exception.resp.status
        return 500 <= status < 600
    
    if hasattr(exception, 'response') and hasattr(exception.response, 'status_code'):
        status = exception.response.status_code
        return 500 <= status < 600
    
    # Check for network-related exceptions
    error_msg = str(exception).lower()
    transient_keywords = [
        'timeout',
        'connection',
        'network',
        'temporary',
        'unavailable',
        'try again'
    ]
    
    return any(keyword in error_msg for keyword in transient_keywords)


# Pre-configured decorators for common use cases
retry_on_network_error = functools.partial(
    retry_on_condition,
    condition=is_transient_error,
    max_retries=3,
    initial_delay=1.0,
    backoff_factor=2.0
)

retry_on_rate_limit = functools.partial(
    retry_on_condition,
    condition=is_rate_limit_error,
    max_retries=5,
    initial_delay=2.0,
    backoff_factor=2.0
)
