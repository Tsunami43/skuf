"""
Тесты для модуля types.
"""
import pytest
from typing import ContextManager, AsyncContextManager, AsyncGenerator, Type, TypeVar

from skuf.dependency.types import (
    T, T_co, 
    ContextManagerFactory, 
    AsyncContextManagerFactory, 
    AsyncGeneratorFactory, 
    Dependency
)


class TestTypes:
    """Тесты для типов в модуле types."""

    def test_dependency_generic_type(self):
        """Тест что Dependency является Generic типом."""
        # Проверяем что Dependency можно параметризовать
        dep_type = Dependency[str]
        assert hasattr(dep_type, '__origin__')
        assert dep_type.__origin__ is Dependency

    def test_dependency_type_vars(self):
        """Тест что T и T_co определены как TypeVar."""
        assert isinstance(T, TypeVar)
        assert isinstance(T_co, TypeVar)
        # Проверяем что это TypeVar объекты
        assert hasattr(T, '__constraints__')
        assert hasattr(T_co, '__constraints__')

    def test_context_manager_factory_protocol(self):
        """Тест протокола ContextManagerFactory."""
        class TestContextManager:
            def __enter__(self):
                return self
            def __exit__(self, exc_type, exc_val, exc_tb):
                pass

        def context_factory() -> ContextManager[TestContextManager]:
            return TestContextManager()

        # Проверяем что функция соответствует протоколу
        assert callable(context_factory)
        result = context_factory()
        assert hasattr(result, '__enter__')
        assert hasattr(result, '__exit__')

    def test_async_context_manager_factory_protocol(self):
        """Тест протокола AsyncContextManagerFactory."""
        class TestAsyncContextManager:
            async def __aenter__(self):
                return self
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        def async_context_factory() -> AsyncContextManager[TestAsyncContextManager]:
            return TestAsyncContextManager()

        # Проверяем что функция соответствует протоколу
        assert callable(async_context_factory)
        result = async_context_factory()
        assert hasattr(result, '__aenter__')
        assert hasattr(result, '__aexit__')

    def test_async_generator_factory_protocol(self):
        """Тест протокола AsyncGeneratorFactory."""
        async def async_generator() -> AsyncGenerator[str, None]:
            yield "test"

        def async_generator_factory() -> AsyncGenerator[str, None]:
            return async_generator()

        # Проверяем что функция соответствует протоколу
        assert callable(async_generator_factory)
        result = async_generator_factory()
        assert hasattr(result, '__aiter__')
        assert hasattr(result, '__anext__')

    def test_dependency_marker_class(self):
        """Тест что Dependency является маркерным классом."""
        # Dependency должен быть классом
        assert isinstance(Dependency, type)
        
        # Проверяем что можно создать экземпляр
        dep = Dependency()
        assert isinstance(dep, Dependency)

    def test_dependency_generic_usage(self):
        """Тест использования Dependency как Generic типа."""
        # Создаем параметризованный тип
        str_dependency = Dependency[str]
        
        # Проверяем что это правильный Generic тип
        assert hasattr(str_dependency, '__origin__')
        assert str_dependency.__origin__ is Dependency
        assert str_dependency.__args__ == (str,)

    def test_dependency_type_hints(self):
        """Тест использования Dependency в аннотациях типов."""
        def test_function(dep: Dependency[str]) -> str:
            return "test"
        
        # Проверяем что аннотация корректна
        annotations = test_function.__annotations__
        assert 'dep' in annotations
        assert annotations['dep'] is Dependency[str]

    def test_context_manager_factory_with_real_context_manager(self):
        """Тест ContextManagerFactory с реальным context manager."""
        class RealContextManager:
            def __init__(self, value: str):
                self.value = value
                self.entered = False
                self.exited = False
                
            def __enter__(self):
                self.entered = True
                return self
                
            def __exit__(self, exc_type, exc_val, exc_tb):
                self.exited = True
                return False

        def context_factory() -> ContextManager[RealContextManager]:
            return RealContextManager("test")

        # Тестируем что фабрика работает
        with context_factory() as cm:
            assert cm.value == "test"
            assert cm.entered is True
        assert cm.exited is True

    def test_async_context_manager_factory_with_real_async_context_manager(self):
        """Тест AsyncContextManagerFactory с реальным async context manager."""
        class RealAsyncContextManager:
            def __init__(self, value: str):
                self.value = value
                self.entered = False
                self.exited = False
                
            async def __aenter__(self):
                self.entered = True
                return self
                
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                self.exited = True
                return False

        def async_context_factory() -> AsyncContextManager[RealAsyncContextManager]:
            return RealAsyncContextManager("test")

        # Тестируем что фабрика работает
        async def test_async_context():
            async with async_context_factory() as cm:
                assert cm.value == "test"
                assert cm.entered is True
            assert cm.exited is True

        import asyncio
        asyncio.run(test_async_context())

    def test_async_generator_factory_with_real_async_generator(self):
        """Тест AsyncGeneratorFactory с реальным async generator."""
        async def real_async_generator() -> AsyncGenerator[str, None]:
            yield "first"
            yield "second"

        def async_generator_factory() -> AsyncGenerator[str, None]:
            return real_async_generator()

        # Тестируем что фабрика работает
        async def test_async_generator():
            gen = async_generator_factory()
            results = []
            async for value in gen:
                results.append(value)
            assert results == ["first", "second"]

        import asyncio
        asyncio.run(test_async_generator())

    def test_dependency_with_different_types(self):
        """Тест Dependency с различными типами."""
        # Строка
        str_dep = Dependency[str]
        assert str_dep.__args__ == (str,)
        
        # Число
        int_dep = Dependency[int]
        assert int_dep.__args__ == (int,)
        
        # Список
        list_dep = Dependency[list]
        assert list_dep.__args__ == (list,)
        
        # Пользовательский класс
        class CustomClass:
            pass
        
        custom_dep = Dependency[CustomClass]
        assert custom_dep.__args__ == (CustomClass,)

    def test_protocol_inheritance(self):
        """Тест что протоколы правильно наследуются."""
        # ContextManagerFactory должен быть протоколом
        assert hasattr(ContextManagerFactory, '__protocol__') or hasattr(ContextManagerFactory, '_is_protocol')
        
        # AsyncContextManagerFactory должен быть протоколом
        assert hasattr(AsyncContextManagerFactory, '__protocol__') or hasattr(AsyncContextManagerFactory, '_is_protocol')
        
        # AsyncGeneratorFactory должен быть протоколом
        assert hasattr(AsyncGeneratorFactory, '__protocol__') or hasattr(AsyncGeneratorFactory, '_is_protocol')

    def test_type_vars_covariance(self):
        """Тест ковариантности TypeVar T_co."""
        # T_co должен быть ковариантным
        assert T_co.__covariant__ is True
        assert T.__covariant__ is False  # T не должен быть ковариантным
