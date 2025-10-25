from typing import Callable, Type, TypeVar, Any
from functools import wraps
import inspect

from .registry import DependencyRegistry
from .inspector import Inspector

T = TypeVar("T")

__all__ = ["Wrapper"]


class Wrapper:
    """Wrappers for automatic dependency context management."""

    @classmethod
    def wrap_function_with_context(
        cls, func: Callable, param_name: str, dependency_cls: Type[T]
    ) -> Callable:
        """Wrap function to automatically handle context managers."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get the dependency
            dependency = DependencyRegistry.resolve(dependency_cls)

            # Get function signature to determine parameter position
            sig = inspect.signature(func)
            param = sig.parameters[param_name]
            
            # Check if parameter is already provided as positional argument
            if param.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
                # Count positional arguments before this parameter
                positional_count = 0
                for p_name, p in sig.parameters.items():
                    if p_name == param_name:
                        break
                    if p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
                        positional_count += 1
                
                # If we have enough positional arguments, don't add to kwargs
                if len(args) > positional_count:
                    return func(*args, **kwargs)

            # Check if it's a context manager
            if Inspector.is_context_manager(dependency):
                with dependency as context_obj:
                    # Replace the parameter with the context object
                    kwargs[param_name] = context_obj
                    return func(*args, **kwargs)
            else:
                # Regular dependency - only add to kwargs if not already provided
                if param_name not in kwargs:
                    kwargs[param_name] = dependency
                return func(*args, **kwargs)

        return wrapper

    @classmethod
    def wrap_async_function_with_context(
        cls, func: Callable, param_name: str, dependency_cls: Type[T]
    ) -> Callable:
        """Wrap async function to automatically handle context managers and generators."""

        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get the dependency
            dependency = DependencyRegistry.resolve(dependency_cls)

            # Get function signature to determine parameter position
            sig = inspect.signature(func)
            param = sig.parameters[param_name]
            
            # Check if parameter is already provided as positional argument
            if param.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
                # Count positional arguments before this parameter
                positional_count = 0
                for p_name, p in sig.parameters.items():
                    if p_name == param_name:
                        break
                    if p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
                        positional_count += 1
                
                # If we have enough positional arguments, don't add to kwargs
                if len(args) > positional_count:
                    return await func(*args, **kwargs)

            # Check if it's an async context manager
            if Inspector.is_async_context_manager(dependency):
                async with dependency as context_obj:
                    kwargs[param_name] = context_obj
                    return await func(*args, **kwargs)
            # Check if it's an async generator
            elif Inspector.is_async_generator(dependency):
                async for context_obj in dependency:
                    kwargs[param_name] = context_obj
                    return await func(*args, **kwargs)
            else:
                # Regular dependency - only add to kwargs if not already provided
                if param_name not in kwargs:
                    kwargs[param_name] = dependency
                return await func(*args, **kwargs)

        return wrapper
