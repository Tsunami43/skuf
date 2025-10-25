from typing import Type, Callable, Dict, Any, Optional, TypeVar

from .types import T

__all__ = ["DependencyRegistry"]


class DependencyRegistry:
    """Dependency registry with support for various factory types."""
    
    __registry: Dict[Type, Callable[[], Any]] = {}

    @classmethod
    def register(
        cls,
        dependency_cls: Type[T],
        *,
        instance: Optional[T] = None,
        factory: Optional[Callable[[], T]] = None,
    ) -> None:
        """
        Register a dependency with the container.

        Args:
            dependency_cls: The class type to register.
            instance: A specific instance to use (singleton-style).
            factory: A factory function to generate the instance.
                     Can be a regular factory, context manager factory, 
                     async context manager factory, or async generator factory.

        Notes:
            Priority: instance > factory > default constructor
        """
        if instance is not None:
            cls.__registry[dependency_cls] = lambda: instance
        elif factory is not None:
            cls.__registry[dependency_cls] = factory
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
        cls.__registry.clear()
