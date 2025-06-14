import warnings
from typing import Type, Callable, Dict, Any, Optional, TypeVar, cast


__all__ = ["Dependency", "DIContainer"]


T = TypeVar("T")


class DIObject:
    pass


class DIContainer(DIObject):
    __registry: Dict[Type, Callable[[], Any]] = {}

    @classmethod
    def register(
        cls,
        dependency_cls: Type[T],
        *,
        instance: Optional[T] = None,
        factory: Optional[Callable[[], T]] = None,
    ):
        """
        Register a dependency.

        :param dependency_cls: The dependency class.
        :param instance: An instance of the dependency.
        :param factory: A factory function that returns an instance of the dependency.
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
        Resolve a dependency.

        :param dependency_cls: The dependency class.
        :return: An instance of the dependency.
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
    def clear(cls):
        warnings.warn("Clearing the registry", stacklevel=2)
        cls.__registry.clear()


def Dependency(_cls: Type[T]) -> T:
    return DIContainer.resolve(_cls)
