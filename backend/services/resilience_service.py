import logging
import time
from typing import Callable, Any, Optional
from functools import wraps
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """Circuit breaker pattern for fault tolerance"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker"""
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half_open"
                logger.info("Circuit breaker: Attempting reset (half-open)")
            else:
                raise Exception(f"Circuit breaker is OPEN. Service unavailable.")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """Handle successful call"""
        if self.state == "half_open":
            self.state = "closed"
            self.failure_count = 0
            logger.info("Circuit breaker: Reset to CLOSED")
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.warning(f"Circuit breaker: Opened after {self.failure_count} failures")
    
    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset"""
        if self.last_failure_time is None:
            return True
        
        return (datetime.now() - self.last_failure_time).seconds >= self.recovery_timeout
    
    def get_state(self) -> dict:
        """Get current circuit breaker state"""
        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "last_failure": self.last_failure_time.isoformat() if self.last_failure_time else None
        }


def retry_with_backoff(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    exceptions: tuple = (Exception,)
):
    """Decorator for retrying functions with exponential backoff"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {str(e)}. "
                            f"Retrying in {delay}s..."
                        )
                        time.sleep(delay)
                        delay = min(delay * backoff_factor, max_delay)
                    else:
                        logger.error(
                            f"All {max_attempts} attempts failed for {func.__name__}: {str(e)}"
                        )
            
            raise last_exception
        
        return wrapper
    return decorator


def timeout(seconds: int):
    """Decorator for adding timeout to functions"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Function {func.__name__} timed out after {seconds}s")
            
            # Set the signal handler
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)
            
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)  # Disable the alarm
            
            return result
        
        return wrapper
    return decorator


class FallbackHandler:
    """Handler for providing fallback responses"""
    
    def __init__(self):
        self.fallback_responses = {}
    
    def register_fallback(self, key: str, response: Any):
        """Register a fallback response"""
        self.fallback_responses[key] = response
        logger.info(f"Registered fallback for: {key}")
    
    def get_fallback(self, key: str, default: Optional[Any] = None) -> Any:
        """Get fallback response"""
        return self.fallback_responses.get(key, default)
    
    def execute_with_fallback(
        self,
        func: Callable,
        fallback_key: str,
        *args,
        **kwargs
    ) -> Any:
        """Execute function with fallback"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Function failed, using fallback: {str(e)}")
            fallback = self.get_fallback(fallback_key)
            
            if fallback is None:
                raise
            
            return fallback


# Global instances
circuit_breakers = {}
fallback_handler = FallbackHandler()


def get_circuit_breaker(name: str, **kwargs) -> CircuitBreaker:
    """Get or create a circuit breaker"""
    if name not in circuit_breakers:
        circuit_breakers[name] = CircuitBreaker(**kwargs)
    return circuit_breakers[name]


# Register default fallback responses
fallback_handler.register_fallback("agent_response", {
    "agent": "System",
    "response": "Le service est temporairement indisponible. Veuillez réessayer dans quelques instants.",
    "sources": [],
    "tool_calls": [],
    "fallback": True
})

fallback_handler.register_fallback("ssh_connection", {
    "success": False,
    "error": "Impossible de se connecter à l'agent distant. Vérifiez la configuration SSH.",
    "fallback": True
})
