import warnings
from typing import Type, Callable, Dict, Any, Optional, TypeVar, cast

__all__ = ["Dependency", "DIContainer"]

T = TypeVar("T")


class DIObject:
    """
    Base class for dependency-injected objects.
    Can be extended in the future to include shared behaviors.
    """

    pass


class DIContainer(DIObject):
    """
    DIContainer is a simple Dependency Injection container.

    It allows registering and resolving dependencies globally, either
    by:
      - passing an instance directly
      - passing a factory function
      - default constructor fallback (no arguments)

    Example usage:

    ```python
    class Service:
        ...

    DIContainer.register(Service)
    service = DIContainer.resolve(Service)
    ```
    """

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
        Register a class and associate it with a factory or fixed instance.

        Args:
            dependency_cls (Type[T]): The class type to register.
            instance (Optional[T]): A specific instance to use (singleton-style).
            factory (Optional[Callable[[], T]]): A factory function to generate the instance.

        Notes:
            - If both `instance` and `factory` are provided, `instance` is used.
            - If none are provided, `dependency_cls()` is used as default factory.
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
        Resolve a previously registered dependency.

        Args:
            dependency_cls (Type[T]): The class type to resolve.

        Returns:
            An instance of the registered dependency.

        Raises:
            ValueError: If the dependency was not registered.
            TypeError: If the resolved instance is not of the correct type.
        """
        if dependency_cls not in cls.__registry:
            raise ValueError(f"Dependency {dependency_cls.__name__} is not registered")

        instance = cls.__registry[dependency_cls]()
        if not isinstance(instance, dependency_cls):
            raise TypeError(
                f"Resolved instance is not of type {dependency_cls.__name__}"
            )
        return cast(T, instance)

    @classmethod
    def clear(cls) -> None:
        """
        Clear the entire registry of dependencies.

        Emits:
            A warning indicating the registry has been cleared.
        """
        warnings.warn("Clearing the registry", stacklevel=2)
        cls.__registry.clear()


def Dependency(_cls: Type[T]) -> T:
    """
    Syntactic sugar function for resolving a dependency.

    Example:
    ```python
    service = Dependency(MyService)
    ```

    Args:
        _cls (Type[T]): The class type to resolve.

    Returns:
        An instance of the dependency.
    """
    return DIContainer.resolve(_cls)
