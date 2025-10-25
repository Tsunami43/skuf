import inspect
from typing import Callable, Any

from .registry import DependencyRegistry
from .wrapper import Wrapper
from .types import Dependency

__all__ = ["Injector"]


class Injector:
    """Автоматический инжектор зависимостей."""

    @classmethod
    def inject(cls, func: Callable) -> Callable:
        """
        Decorator to automatically inject dependencies into function parameters.

        Example:
        ```python
        @Dependency.inject
        def my_function(uow: IUnitOfWork = Dependency(IUnitOfWork)):
            uow.add_operation("test")
        ```
        """
        if not callable(func):
            raise TypeError("inject decorator can only be applied to callable objects")

        # Get function signature
        sig = inspect.signature(func)

        # Check if function is async
        is_async = inspect.iscoroutinefunction(func)

        # Find parameters with Dependency annotations
        for param_name, param in sig.parameters.items():
            if param.annotation != inspect.Parameter.empty:
                # Check if parameter has Dependency annotation
                if (
                    hasattr(param.annotation, "__origin__")
                    and param.annotation.__origin__ is Dependency
                ):
                    dependency_cls = param.annotation.__args__[0]

                    if is_async:
                        func = Wrapper.wrap_async_function_with_context(
                            func, param_name, dependency_cls
                        )
                    else:
                        func = Wrapper.wrap_function_with_context(
                            func, param_name, dependency_cls
                        )
                # Also check for direct Dependency annotation (for backward compatibility)
                elif param.annotation is Dependency:
                    # This is a fallback for cases where Dependency is used directly
                    # We need to get the type from the default value or raise an error
                    if param.default != inspect.Parameter.empty:
                        # Try to get the type from the default value
                        if hasattr(param.default, "__class__"):
                            dependency_cls = param.default.__class__
                        else:
                            continue
                    else:
                        continue

                    if is_async:
                        func = Wrapper.wrap_async_function_with_context(
                            func, param_name, dependency_cls
                        )
                    else:
                        func = Wrapper.wrap_function_with_context(
                            func, param_name, dependency_cls
                        )

        return func
