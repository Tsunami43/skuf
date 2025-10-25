"""
Dependency Injection модуль.

Собирает все компоненты в единый класс Dependency для удобного использования.
"""

from typing import Type, TypeVar, Generic

from .types import T, Dependency as DependencyType
from .registry import DependencyRegistry
from .injector import Injector

__all__ = ["Dependency"]


class Dependency(Generic[T]):
    """
    Главный класс для работы с dependency injection.
    Объединяет функциональность регистрации, разрешения и инъекции зависимостей.
    
    Используется как:
    1. Маркер типа в аннотациях: Dependency[SomeClass]
    2. Класс для регистрации/разрешения зависимостей
    """

    @classmethod
    def register(cls, dependency_cls: Type[T], **kwargs) -> None:
        """Регистрирует зависимость."""
        DependencyRegistry.register(dependency_cls, **kwargs)

    @classmethod
    def resolve(cls, dependency_cls: Type[T]) -> T:
        """Разрешает зависимость."""
        return DependencyRegistry.resolve(dependency_cls)

    @classmethod
    def clear(cls) -> None:
        """Очищает реестр зависимостей."""
        DependencyRegistry.clear()

    @classmethod
    def inject(cls, func):
        """Декоратор для автоматической инъекции зависимостей."""
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
