import warnings
from typing import Type, Callable, Dict, Any, Optional, TypeVar

from .types import T, ContextManagerFactory, AsyncContextManagerFactory, AsyncGeneratorFactory

__all__ = ["DependencyRegistry"]


class DependencyRegistry:
    """Реестр зависимостей с поддержкой различных фабрик."""
    
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
