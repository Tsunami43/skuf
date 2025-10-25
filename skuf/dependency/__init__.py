"""
Dependency Injection module.

Combines all components into a single Dependency class for convenient usage.
"""

from typing import Callable, Optional, Type, TypeVar, Generic

from .types import T, Dependency as DependencyType
from .registry import DependencyRegistry
from .injector import Injector

__all__ = ["Dependency"]


class Dependency(Generic[T]):
    """
    Main class for dependency injection.
    Combines functionality for registration, resolution and injection of dependencies.
    
    Used as:
    1. Type marker in annotations: Dependency[SomeClass]
    2. Class for registering/resolving dependencies
    """

    @classmethod
    def register(cls, dependency_cls: Type[T], *,
        instance: Optional[T] = None,
        factory: Optional[Callable[[], T]] = None) -> None:
        """Register a dependency."""
        DependencyRegistry.register(dependency_cls, instance=instance, factory=factory)

    @classmethod
    def resolve(cls, dependency_cls: Type[T]) -> T:
        """Resolve a dependency."""
        return DependencyRegistry.resolve(dependency_cls)

    @classmethod
    def clear(cls) -> None:
        """Clear the dependency registry."""
        DependencyRegistry.clear()

    @classmethod
    def inject(cls, func):
        """Decorator for automatic dependency injection."""
        return Injector.inject(func)

    @classmethod
    def __class_getitem__(cls, dependency_cls: Type[T]) -> Type[DependencyType[T]]:
        """
        Support for Dependency[SomeClass] syntax.

        Example:
        ```python
        def my_function(uow: Dependency[IUnitOfWork]):
            uow.add_operation("test")
        ```
        """
        # Return the DependencyType from types module for proper type checking
        return DependencyType[dependency_cls]
