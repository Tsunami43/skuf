"""
Тесты для модуля injector.
"""
import pytest
from unittest.mock import Mock, patch
from typing import AsyncGenerator

from skuf.dependency.injector import Injector
from skuf.dependency.registry import DependencyRegistry
from skuf.dependency.types import Dependency


class TestInjector:
    """Тесты для класса Injector."""

    def test_inject_with_non_callable_raises_error(self):
        """Тест что inject с не-callable объектом вызывает ошибку."""
        with pytest.raises(TypeError, match="inject decorator can only be applied to callable objects"):
            Injector.inject("not a function")

    def test_inject_with_regular_function_no_dependencies(self):
        """Тест inject с обычной функцией без зависимостей."""
        def test_func():
            return "test"
        
        wrapped_func = Injector.inject(test_func)
        
        # Функция должна работать как обычно
        result = wrapped_func()
        assert result == "test"

    def test_inject_with_async_function_no_dependencies(self):
        """Тест inject с async функцией без зависимостей."""
        import asyncio
        
        async def test_func():
            return "test"
        
        wrapped_func = Injector.inject(test_func)
        
        # Функция должна работать как обычно
        result = asyncio.run(wrapped_func())
        assert result == "test"

    def test_inject_with_dependency_annotation(self, sample_class):
        """Тест inject с аннотацией Dependency."""
        instance = sample_class("test_value")
        DependencyRegistry.register(sample_class, instance=instance)
        
        def test_func(dep: Dependency[sample_class]):
            return dep.get_value()
        
        wrapped_func = Injector.inject(test_func)
        result = wrapped_func()
        assert result == "test_value"

    @pytest.mark.asyncio
    async def test_inject_with_async_function_dependency_annotation(self, sample_class):
        """Тест inject с async функцией и аннотацией Dependency."""
        instance = sample_class("test_value")
        DependencyRegistry.register(sample_class, instance=instance)
        
        async def test_func(dep: Dependency[sample_class]):
            return dep.get_value()
        
        wrapped_func = Injector.inject(test_func)
        result = await wrapped_func()
        assert result == "test_value"

    def test_inject_with_context_manager_dependency(self, context_manager_class):
        """Тест inject с context manager зависимостью."""
        def context_factory():
            return context_manager_class("context_value")
        
        DependencyRegistry.register(context_manager_class, context_manager=context_factory)
        
        def test_func(dep: Dependency[context_manager_class]):
            return dep.value
        
        wrapped_func = Injector.inject(test_func)
        result = wrapped_func()
        assert result == "context_value"

    @pytest.mark.asyncio
    async def test_inject_with_async_context_manager_dependency(self, async_context_manager_class):
        """Тест inject с async context manager зависимостью."""
        def async_context_factory():
            return async_context_manager_class("async_context_value")
        
        DependencyRegistry.register(async_context_manager_class, async_context_manager=async_context_factory)
        
        async def test_func(dep: Dependency[async_context_manager_class]):
            return dep.value
        
        wrapped_func = Injector.inject(test_func)
        result = await wrapped_func()
        assert result == "async_context_value"

    @pytest.mark.asyncio
    async def test_inject_with_async_generator_dependency(self, async_generator_class):
        """Тест inject с async generator зависимостью."""
        def async_generator_factory():
            return async_generator_class("async_generator_value")
        
        DependencyRegistry.register(async_generator_class, async_generator_factory=async_generator_factory)
        
        async def test_func(dep: Dependency[async_generator_class]):
            return dep.value
        
        wrapped_func = Injector.inject(test_func)
        result = await wrapped_func()
        assert result == "async_generator_value"

    def test_inject_with_multiple_dependencies(self, sample_class, context_manager_class):
        """Тест inject с несколькими зависимостями."""
        instance1 = sample_class("value1")
        instance2 = context_manager_class("value2")
        
        DependencyRegistry.register(sample_class, instance=instance1)
        DependencyRegistry.register(context_manager_class, instance=instance2)
        
        def test_func(dep1: Dependency[sample_class], dep2: Dependency[context_manager_class]):
            return f"{dep1.get_value()}_{dep2.value}"
        
        wrapped_func = Injector.inject(test_func)
        result = wrapped_func()
        assert result == "value1_value2"

    def test_inject_with_mixed_parameters(self, sample_class):
        """Тест inject с смешанными параметрами (с зависимостями и без)."""
        instance = sample_class("test_value")
        DependencyRegistry.register(sample_class, instance=instance)
        
        def test_func(regular_param: str, dep: Dependency[sample_class], another_regular: int):
            return f"{regular_param}_{dep.get_value()}_{another_regular}"
        
        wrapped_func = Injector.inject(test_func)
        result = wrapped_func("hello", 42)
        assert result == "hello_test_value_42"

    def test_inject_preserves_function_metadata(self, sample_class):
        """Тест что inject сохраняет метаданные функции."""
        instance = sample_class("test_value")
        DependencyRegistry.register(sample_class, instance=instance)
        
        def test_func(dep: Dependency[sample_class]):
            """Test function docstring."""
            return dep.get_value()
        
        test_func.__name__ = "test_function"
        test_func.__module__ = "test_module"
        
        wrapped_func = Injector.inject(test_func)
        
        # Проверяем что метаданные сохранены
        assert wrapped_func.__name__ == "test_function"
        assert wrapped_func.__module__ == "test_module"
        assert wrapped_func.__doc__ == "Test function docstring."

    def test_inject_with_no_annotation_parameters(self):
        """Тест inject с параметрами без аннотаций."""
        def test_func(param1, param2):
            return f"{param1}_{param2}"
        
        wrapped_func = Injector.inject(test_func)
        result = wrapped_func("hello", "world")
        assert result == "hello_world"

    def test_inject_with_empty_annotation_parameters(self):
        """Тест inject с параметрами с пустыми аннотациями."""
        def test_func(param1: str, param2: int):
            return f"{param1}_{param2}"
        
        wrapped_func = Injector.inject(test_func)
        result = wrapped_func("hello", 42)
        assert result == "hello_42"

    def test_inject_with_non_dependency_annotations(self):
        """Тест inject с аннотациями, не являющимися Dependency."""
        def test_func(param1: str, param2: int):
            return f"{param1}_{param2}"
        
        wrapped_func = Injector.inject(test_func)
        result = wrapped_func("hello", 42)
        assert result == "hello_42"

    def test_inject_with_unregistered_dependency_raises_error(self, sample_class):
        """Тест что inject с незарегистрированной зависимостью вызывает ошибку."""
        def test_func(dep: Dependency[sample_class]):
            return dep.get_value()
        
        wrapped_func = Injector.inject(test_func)
        
        with pytest.raises(ValueError, match="Dependency .* is not registered"):
            wrapped_func()

    @pytest.mark.asyncio
    async def test_inject_with_async_function_unregistered_dependency_raises_error(self, sample_class):
        """Тест что inject с async функцией и незарегистрированной зависимостью вызывает ошибку."""
        async def test_func(dep: Dependency[sample_class]):
            return dep.get_value()
        
        wrapped_func = Injector.inject(test_func)
        
        with pytest.raises(ValueError, match="Dependency .* is not registered"):
            await wrapped_func()

    def test_inject_with_kwargs_preserved(self, sample_class):
        """Тест что inject сохраняет kwargs."""
        instance = sample_class("test_value")
        DependencyRegistry.register(sample_class, instance=instance)
        
        def test_func(dep: Dependency[sample_class], **kwargs):
            return f"{dep.get_value()}_{kwargs.get('extra', 'none')}"
        
        wrapped_func = Injector.inject(test_func)
        result = wrapped_func(extra="data")
        assert result == "test_value_data"

    def test_inject_with_args_and_kwargs_preserved(self, sample_class):
        """Тест что inject сохраняет args и kwargs."""
        instance = sample_class("test_value")
        DependencyRegistry.register(sample_class, instance=instance)
        
        def test_func(*args, dep: Dependency[sample_class], **kwargs):
            return f"{args}_{dep.get_value()}_{kwargs.get('extra', 'none')}"
        
        wrapped_func = Injector.inject(test_func)
        result = wrapped_func("arg1", "arg2", extra="data")
        assert result == "('arg1', 'arg2')_test_value_data"

    @pytest.mark.asyncio
    async def test_inject_with_async_function_args_and_kwargs_preserved(self, sample_class):
        """Тест что inject с async функцией сохраняет args и kwargs."""
        instance = sample_class("test_value")
        DependencyRegistry.register(sample_class, instance=instance)
        
        async def test_func(*args, dep: Dependency[sample_class], **kwargs):
            return f"{args}_{dep.get_value()}_{kwargs.get('extra', 'none')}"
        
        wrapped_func = Injector.inject(test_func)
        result = await wrapped_func("arg1", "arg2", extra="data")
        assert result == "('arg1', 'arg2')_test_value_data"

    def test_inject_with_class_method(self, sample_class):
        """Тест inject с методом класса."""
        instance = sample_class("test_value")
        DependencyRegistry.register(sample_class, instance=instance)
        
        class TestClass:
            def test_method(self, dep: Dependency[sample_class]):
                return dep.get_value()
        
        test_instance = TestClass()
        wrapped_method = Injector.inject(test_instance.test_method)
        result = wrapped_method()
        assert result == "test_value"

    def test_inject_with_static_method(self, sample_class):
        """Тест inject со статическим методом."""
        instance = sample_class("test_value")
        DependencyRegistry.register(sample_class, instance=instance)
        
        class TestClass:
            @staticmethod
            def test_method(dep: Dependency[sample_class]):
                return dep.get_value()
        
        wrapped_method = Injector.inject(TestClass.test_method)
        result = wrapped_method()
        assert result == "test_value"

    def test_inject_with_lambda(self, sample_class):
        """Тест inject с lambda функцией."""
        instance = sample_class("test_value")
        DependencyRegistry.register(sample_class, instance=instance)
        
        test_lambda = lambda dep: dep.get_value()
        test_lambda.__annotations__ = {'dep': Dependency[sample_class]}
        
        wrapped_lambda = Injector.inject(test_lambda)
        result = wrapped_lambda()
        assert result == "test_value"
