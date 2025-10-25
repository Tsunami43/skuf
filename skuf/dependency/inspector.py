from typing import Any

__all__ = ["Inspector"]


class Inspector:
    """Utilities for checking object types."""

    @staticmethod
    def is_context_manager(obj: Any) -> bool:
        """Check if object is a context manager."""
        return hasattr(obj, "__enter__") and hasattr(obj, "__exit__")

    @staticmethod
    def is_async_context_manager(obj: Any) -> bool:
        """Check if object is an async context manager."""
        return hasattr(obj, "__aenter__") and hasattr(obj, "__aexit__")

    @staticmethod
    def is_async_generator(obj: Any) -> bool:
        """Check if object is an async generator."""
        return hasattr(obj, "__aiter__") and hasattr(obj, "__anext__")
