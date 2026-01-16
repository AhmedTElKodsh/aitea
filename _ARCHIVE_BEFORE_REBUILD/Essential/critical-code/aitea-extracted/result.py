"""Result type pattern for explicit error handling.

This module provides a Result[T, E] generic class that represents
either a successful value (Ok) or an error (Err), enabling explicit
error handling without exceptions.
"""

from dataclasses import dataclass
from typing import Generic, TypeVar, Union, Callable, Optional

T = TypeVar('T')  # Success type
E = TypeVar('E')  # Error type
U = TypeVar('U')  # Mapped success type


class UnwrapError(Exception):
    """Raised when unwrapping a Result in an invalid state."""
    pass


@dataclass(frozen=True)
class Ok(Generic[T]):
    """Represents a successful result containing a value."""
    _value: T
    
    @property
    def value(self) -> T:
        """Get the success value."""
        return self._value


@dataclass(frozen=True)
class Err(Generic[E]):
    """Represents an error result containing an error."""
    _error: E
    
    @property
    def error(self) -> E:
        """Get the error value."""
        return self._error


class Result(Generic[T, E]):
    """A discriminated union for success/error handling.
    
    Result[T, E] represents either:
    - A successful value of type T (Ok)
    - An error of type E (Err)
    
    This pattern enables explicit error handling without exceptions,
    making error cases visible in function signatures and forcing
    callers to handle both success and error cases.
    
    Example:
        >>> result = Result.ok(42)
        >>> if result.is_ok():
        ...     print(f"Success: {result.unwrap()}")
        Success: 42
        
        >>> result = Result.err(ValidationError("name", "required", None))
        >>> if result.is_err():
        ...     print(f"Error: {result.unwrap_err()}")
        Error: Validation error on 'name': required (got: None)
    """
    
    __slots__ = ('_inner',)
    
    def __init__(self, inner: Union[Ok[T], Err[E]]) -> None:
        """Initialize with an Ok or Err value.
        
        Use the static methods ok() and err() instead of direct construction.
        """
        self._inner = inner
    
    @staticmethod
    def ok(value: T) -> 'Result[T, E]':
        """Create a successful Result containing the given value.
        
        Args:
            value: The success value to wrap
            
        Returns:
            A Result in the Ok state
        """
        return Result(Ok(value))
    
    @staticmethod
    def err(error: E) -> 'Result[T, E]':
        """Create an error Result containing the given error.
        
        Args:
            error: The error value to wrap
            
        Returns:
            A Result in the Err state
        """
        return Result(Err(error))
    
    def is_ok(self) -> bool:
        """Check if this Result is a success.
        
        Returns:
            True if this Result contains a success value, False otherwise
        """
        return isinstance(self._inner, Ok)
    
    def is_err(self) -> bool:
        """Check if this Result is an error.
        
        Returns:
            True if this Result contains an error, False otherwise
        """
        return isinstance(self._inner, Err)
    
    def unwrap(self) -> T:
        """Extract the success value.
        
        Returns:
            The success value if this Result is Ok
            
        Raises:
            UnwrapError: If this Result is an Err
        """
        if isinstance(self._inner, Ok):
            return self._inner.value
        raise UnwrapError(f"Called unwrap() on an Err value: {self._inner.error}")
    
    def unwrap_err(self) -> E:
        """Extract the error value.
        
        Returns:
            The error value if this Result is Err
            
        Raises:
            UnwrapError: If this Result is an Ok
        """
        if isinstance(self._inner, Err):
            return self._inner.error
        raise UnwrapError(f"Called unwrap_err() on an Ok value: {self._inner.value}")
    
    def unwrap_or(self, default: T) -> T:
        """Extract the success value or return a default.
        
        Args:
            default: Value to return if this Result is an Err
            
        Returns:
            The success value if Ok, otherwise the default
        """
        if isinstance(self._inner, Ok):
            return self._inner.value
        return default
    
    def unwrap_or_else(self, f: Callable[[E], T]) -> T:
        """Extract the success value or compute from the error.
        
        Args:
            f: Function to compute a value from the error
            
        Returns:
            The success value if Ok, otherwise f(error)
        """
        if isinstance(self._inner, Ok):
            return self._inner.value
        return f(self._inner.error)
    
    def map(self, f: Callable[[T], U]) -> 'Result[U, E]':
        """Transform the success value if present.
        
        Args:
            f: Function to apply to the success value
            
        Returns:
            A new Result with the transformed value if Ok,
            otherwise the original Err
        """
        if isinstance(self._inner, Ok):
            return Result.ok(f(self._inner.value))
        return Result(self._inner)
    
    def map_err(self, f: Callable[[E], U]) -> 'Result[T, U]':
        """Transform the error value if present.
        
        Args:
            f: Function to apply to the error value
            
        Returns:
            A new Result with the transformed error if Err,
            otherwise the original Ok
        """
        if isinstance(self._inner, Err):
            return Result.err(f(self._inner.error))
        return Result(self._inner)
    
    def and_then(self, f: Callable[[T], 'Result[U, E]']) -> 'Result[U, E]':
        """Chain operations that may fail.
        
        Args:
            f: Function that takes the success value and returns a new Result
            
        Returns:
            The result of f(value) if Ok, otherwise the original Err
        """
        if isinstance(self._inner, Ok):
            return f(self._inner.value)
        return Result(self._inner)
    
    def or_else(self, f: Callable[[E], 'Result[T, U]']) -> 'Result[T, U]':
        """Provide an alternative Result on error.
        
        Args:
            f: Function that takes the error and returns a new Result
            
        Returns:
            The original Ok if successful, otherwise f(error)
        """
        if isinstance(self._inner, Ok):
            return Result(self._inner)
        return f(self._inner.error)
    
    def __repr__(self) -> str:
        """Return a string representation."""
        if isinstance(self._inner, Ok):
            return f"Result.ok({self._inner.value!r})"
        return f"Result.err({self._inner.error!r})"
    
    def __eq__(self, other: object) -> bool:
        """Check equality with another Result."""
        if not isinstance(other, Result):
            return NotImplemented
        return self._inner == other._inner
    
    def __hash__(self) -> int:
        """Return hash of the inner value."""
        return hash(self._inner)
