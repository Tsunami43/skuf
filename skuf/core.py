import warnings
import inspect
import asyncio
from typing import Type, Callable, Dict, Any, Optional, TypeVar, cast, Union, AsyncContextManager, ContextManager, AsyncGenerator, get_type_hints
from contextlib import asynccontextmanager, contextmanager
from functools import wraps

# Protocol compatibility for Python 3.7
try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol

__all__ = ["Dependency"]

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)


class ContextManagerFactory(Protocol[T_co]):
    def __call__(self) -> ContextManager[T_co]: ...


class AsyncContextManagerFactory(Protocol[T_co]):
    def __call__(self) -> AsyncContextManager[T_co]: ...


class AsyncGeneratorFactory(Protocol[T_co]):
    def __call__(self) -> AsyncGenerator[T_co, None]: ...


class Dependency:
    """
    Dependency injection with automatic context management.
    
    Supports:
    - Regular dependencies
    - Context managers (with automatic cleanup)
    - Async context managers (with automatic cleanup)
    - Async generators (with automatic cleanup)
    """
    
    __registry: Dict[Type, Callable[[], Any]] = {}
    
    @classmethod
    def register(
        cls,
        dependency_cls: Type[T],
        *,
        instance: Optional[T] = None,
        factory: Optional[Callable[[], T]] = None,
        context_manager: Optional[ContextManagerFactory[T]] = None,
        async_context_manager: Optional[AsyncContextManagerFactory[T]] = None,
        async_generator_factory: Optional[AsyncGeneratorFactory[T]] = None,
    ) -> None:
        """
        Register a dependency with the container.

        Args:
            dependency_cls: The class type to register.
            instance: A specific instance to use (singleton-style).
            factory: A factory function to generate the instance.
            context_manager: A context manager factory.
            async_context_manager: An async context manager factory.
            async_generator_factory: An async generator factory.

        Notes:
            Priority: instance > factory > context_manager > async_context_manager > async_generator_factory > default constructor
        """
        if instance is not None:
            cls.__registry[dependency_cls] = lambda: instance
        elif factory is not None:
            cls.__registry[dependency_cls] = factory
        elif context_manager is not None:
            cls.__registry[dependency_cls] = context_manager
        elif async_context_manager is not None:
            cls.__registry[dependency_cls] = async_context_manager
        elif async_generator_factory is not None:
            cls.__registry[dependency_cls] = async_generator_factory
        else:
            cls.__registry[dependency_cls] = lambda: dependency_cls()

    @classmethod
    def resolve(cls, dependency_cls: Type[T]) -> T:
        """
        Resolve a dependency from the container.

        Args:
            dependency_cls: The class type to resolve.

        Returns:
            An instance of the dependency.

        Raises:
            ValueError: If the dependency was not registered.
        """
        if dependency_cls not in cls.__registry:
            raise ValueError(f"Dependency {dependency_cls.__name__} is not registered")

        factory = cls.__registry[dependency_cls]
        return factory()

    @classmethod
    def clear(cls) -> None:
        """Clear the entire registry of dependencies."""
        warnings.warn("Clearing the registry", stacklevel=2)
        cls.__registry.clear()

    @classmethod
    def _is_context_manager(cls, obj: Any) -> bool:
        """Check if object is a context manager."""
        return hasattr(obj, '__enter__') and hasattr(obj, '__exit__')

    @classmethod
    def _is_async_context_manager(cls, obj: Any) -> bool:
        """Check if object is an async context manager."""
        return hasattr(obj, '__aenter__') and hasattr(obj, '__aexit__')

    @classmethod
    def _is_async_generator(cls, obj: Any) -> bool:
        """Check if object is an async generator."""
        return hasattr(obj, '__aiter__') and hasattr(obj, '__anext__')

    @classmethod
    def _wrap_function_with_context(cls, func: Callable, param_name: str, dependency_cls: Type[T]) -> Callable:
        """Wrap function to automatically handle context managers."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get the dependency
            dependency = cls.resolve(dependency_cls)
            
            # Check if it's a context manager
            if cls._is_context_manager(dependency):
                with dependency as context_obj:
                    # Replace the parameter with the context object
                    kwargs[param_name] = context_obj
                    return func(*args, **kwargs)
            else:
                # Regular dependency
                kwargs[param_name] = dependency
                return func(*args, **kwargs)
        
        return wrapper

    @classmethod
    def _wrap_async_function_with_context(cls, func: Callable, param_name: str, dependency_cls: Type[T]) -> Callable:
        """Wrap async function to automatically handle context managers and generators."""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get the dependency
            dependency = cls.resolve(dependency_cls)
            
            # Check if it's an async context manager
            if cls._is_async_context_manager(dependency):
                async with dependency as context_obj:
                    kwargs[param_name] = context_obj
                    return await func(*args, **kwargs)
            # Check if it's an async generator
            elif cls._is_async_generator(dependency):
                async for context_obj in dependency:
                    kwargs[param_name] = context_obj
                    return await func(*args, **kwargs)
            else:
                # Regular dependency
                kwargs[param_name] = dependency
                return await func(*args, **kwargs)
        
        return wrapper

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
                if hasattr(param.annotation, '__origin__') and param.annotation.__origin__ is Dependency:
                    dependency_cls = param.annotation.__args__[0]
                    
                    if is_async:
                        func = cls._wrap_async_function_with_context(func, param_name, dependency_cls)
                    else:
                        func = cls._wrap_function_with_context(func, param_name, dependency_cls)
        
        return func

    def __class_getitem__(cls, dependency_cls: Type[T]) -> Type[T]:
        """
        Support for Dependency[SomeClass] syntax.
        
        Example:
        ```python
        def my_function(uow: Dependency[IUnitOfWork]):
            uow.add_operation("test")
        ```
        """
        return dependency_cls
