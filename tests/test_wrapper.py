"""
Тесты для модуля wrapper.
"""
import pytest
from unittest.mock import Mock, patch
from typing import AsyncGenerator

from skuf.dependency.wrapper import Wrapper
from skuf.dependency.registry import DependencyRegistry
from skuf.dependency.inspector import Inspector


class TestWrapper:
    """Тесты для класса Wrapper."""

    def test_wrap_function_with_context_regular_dependency(self, sample_class):
        """Тест обертки функции с обычной зависимостью."""
        instance = sample_class("test_value")
        DependencyRegistry.register(sample_class, instance=instance)
        
        def test_func(dep: sample_class):
            return dep.get_value()
        
        wrapped_func = Wrapper.wrap_function_with_context(test_func, "dep", sample_class)
        
        result = wrapped_func()
        assert result == "test_value"

    def test_wrap_function_with_context_context_manager(self, context_manager_class):
        """Тест обертки функции с context manager."""
        def context_factory():
            return context_manager_class("context_value")
        
        DependencyRegistry.register(context_manager_class, context_manager=context_factory)
        
        def test_func(dep: context_manager_class):
            return dep.value
        
        wrapped_func = Wrapper.wrap_function_with_context(test_func, "dep", context_manager_class)
        
        result = wrapped_func()
        assert result == "context_value"

    def test_wrap_function_with_context_manager_enters_and_exits(self, context_manager_class):
        """Тест что context manager правильно входит и выходит."""
        def context_factory():
            return context_manager_class("test")
        
        DependencyRegistry.register(context_manager_class, context_manager=context_factory)
        
        def test_func(dep: context_manager_class):
            # dep должен быть результатом __enter__, а не самим context manager
            return dep.entered, dep.exited
        
        wrapped_func = Wrapper.wrap_function_with_context(test_func, "dep", context_manager_class)
        
        entered, exited = wrapped_func()
        assert entered is True
        # Context manager должен быть закрыт после выхода из with блока
        assert exited is True

    def test_wrap_function_with_context_preserves_original_args(self, sample_class):
        """Тест что обертка сохраняет оригинальные аргументы."""
        instance = sample_class("test_value")
        DependencyRegistry.register(sample_class, instance=instance)
        
        def test_func(arg1: str, arg2: int, dep: sample_class):
            return f"{arg1}_{arg2}_{dep.get_value()}"
        
        wrapped_func = Wrapper.wrap_function_with_context(test_func, "dep", sample_class)
        
        result = wrapped_func("hello", 42)
        assert result == "hello_42_test_value"

    def test_wrap_function_with_context_preserves_kwargs(self, sample_class):
        """Тест что обертка сохраняет kwargs."""
        instance = sample_class("test_value")
        DependencyRegistry.register(sample_class, instance=instance)
        
        def test_func(dep: sample_class, **kwargs):
            return f"{dep.get_value()}_{kwargs.get('extra', 'none')}"
        
        wrapped_func = Wrapper.wrap_function_with_context(test_func, "dep", sample_class)
        
        result = wrapped_func(extra="data")
        assert result == "test_value_data"

    @pytest.mark.asyncio
    async def test_wrap_async_function_with_context_regular_dependency(self, sample_class):
        """Тест обертки async функции с обычной зависимостью."""
        instance = sample_class("test_value")
        DependencyRegistry.register(sample_class, instance=instance)
        
        async def test_func(dep: sample_class):
            return dep.get_value()
        
        wrapped_func = Wrapper.wrap_async_function_with_context(test_func, "dep", sample_class)
        
        result = await wrapped_func()
        assert result == "test_value"

    @pytest.mark.asyncio
    async def test_wrap_async_function_with_context_async_context_manager(self, async_context_manager_class):
        """Тест обертки async функции с async context manager."""
        def async_context_factory():
            return async_context_manager_class("async_context_value")
        
        DependencyRegistry.register(async_context_manager_class, async_context_manager=async_context_factory)
        
        async def test_func(dep: async_context_manager_class):
            return dep.value
        
        wrapped_func = Wrapper.wrap_async_function_with_context(test_func, "dep", async_context_manager_class)
        
        result = await wrapped_func()
        assert result == "async_context_value"

    @pytest.mark.asyncio
    async def test_wrap_async_function_with_context_manager_enters_and_exits(self, async_context_manager_class):
        """Тест что async context manager правильно входит и выходит."""
        def async_context_factory():
            return async_context_manager_class("test")
        
        DependencyRegistry.register(async_context_manager_class, async_context_manager=async_context_factory)
        
        async def test_func(dep: async_context_manager_class):
            return dep.entered, dep.exited
        
        wrapped_func = Wrapper.wrap_async_function_with_context(test_func, "dep", async_context_manager_class)
        
        entered, exited = await wrapped_func()
        assert entered is True
        assert exited is True

    @pytest.mark.asyncio
    async def test_wrap_async_function_with_async_generator(self, async_generator_class):
        """Тест обертки async функции с async generator."""
        def async_generator_factory():
            return async_generator_class("async_generator_value")
        
        DependencyRegistry.register(async_generator_class, async_generator_factory=async_generator_factory)
        
        async def test_func(dep: async_generator_class):
            return dep.value
        
        wrapped_func = Wrapper.wrap_async_function_with_context(test_func, "dep", async_generator_class)
        
        result = await wrapped_func()
        assert result == "async_generator_value"

    @pytest.mark.asyncio
    async def test_wrap_async_function_preserves_original_args(self, sample_class):
        """Тест что async обертка сохраняет оригинальные аргументы."""
        instance = sample_class("test_value")
        DependencyRegistry.register(sample_class, instance=instance)
        
        async def test_func(arg1: str, arg2: int, dep: sample_class):
            return f"{arg1}_{arg2}_{dep.get_value()}"
        
        wrapped_func = Wrapper.wrap_async_function_with_context(test_func, "dep", sample_class)
        
        result = await wrapped_func("hello", 42)
        assert result == "hello_42_test_value"

    @pytest.mark.asyncio
    async def test_wrap_async_function_preserves_kwargs(self, sample_class):
        """Тест что async обертка сохраняет kwargs."""
        instance = sample_class("test_value")
        DependencyRegistry.register(sample_class, instance=instance)
        
        async def test_func(dep: sample_class, **kwargs):
            return f"{dep.get_value()}_{kwargs.get('extra', 'none')}"
        
        wrapped_func = Wrapper.wrap_async_function_with_context(test_func, "dep", sample_class)
        
        result = await wrapped_func(extra="data")
        assert result == "test_value_data"

    def test_wrap_function_with_context_exception_handling(self, context_manager_class):
        """Тест обработки исключений в context manager."""
        def context_factory():
            return context_manager_class("test")
        
        DependencyRegistry.register(context_manager_class, context_manager=context_factory)
        
        def test_func(dep: context_manager_class):
            raise ValueError("test error")
        
        wrapped_func = Wrapper.wrap_function_with_context(test_func, "dep", context_manager_class)
        
        with pytest.raises(ValueError, match="test error"):
            wrapped_func()

    @pytest.mark.asyncio
    async def test_wrap_async_function_with_context_exception_handling(self, async_context_manager_class):
        """Тест обработки исключений в async context manager."""
        def async_context_factory():
            return async_context_manager_class("test")
        
        DependencyRegistry.register(async_context_manager_class, async_context_manager=async_context_factory)
        
        async def test_func(dep: async_context_manager_class):
            raise ValueError("test error")
        
        wrapped_func = Wrapper.wrap_async_function_with_context(test_func, "dep", async_context_manager_class)
        
        with pytest.raises(ValueError, match="test error"):
            await wrapped_func()

    def test_wrap_function_with_context_registry_error(self, sample_class):
        """Тест обработки ошибки реестра в обертке."""
        def test_func(dep: sample_class):
            return dep.get_value()
        
        wrapped_func = Wrapper.wrap_function_with_context(test_func, "dep", sample_class)
        
        with pytest.raises(ValueError, match="Dependency .* is not registered"):
            wrapped_func()

    @pytest.mark.asyncio
    async def test_wrap_async_function_with_context_registry_error(self, sample_class):
        """Тест обработки ошибки реестра в async обертке."""
        async def test_func(dep: sample_class):
            return dep.get_value()
        
        wrapped_func = Wrapper.wrap_async_function_with_context(test_func, "dep", sample_class)
        
        with pytest.raises(ValueError, match="Dependency .* is not registered"):
            await wrapped_func()

    def test_wrap_function_with_context_preserves_function_metadata(self, sample_class):
        """Тест что обертка сохраняет метаданные функции."""
        instance = sample_class("test_value")
        DependencyRegistry.register(sample_class, instance=instance)
        
        def test_func(dep: sample_class):
            """Test function docstring."""
            return dep.get_value()
        
        test_func.__name__ = "test_function"
        test_func.__module__ = "test_module"
        
        wrapped_func = Wrapper.wrap_function_with_context(test_func, "dep", sample_class)
        
        # Проверяем что functools.wraps сохранил метаданные
        assert wrapped_func.__name__ == "test_function"
        assert wrapped_func.__module__ == "test_module"
        assert wrapped_func.__doc__ == "Test function docstring."

    @pytest.mark.asyncio
    async def test_wrap_async_function_with_context_preserves_function_metadata(self, sample_class):
        """Тест что async обертка сохраняет метаданные функции."""
        instance = sample_class("test_value")
        DependencyRegistry.register(sample_class, instance=instance)
        
        async def test_func(dep: sample_class):
            """Test async function docstring."""
            return dep.get_value()
        
        test_func.__name__ = "test_async_function"
        test_func.__module__ = "test_module"
        
        wrapped_func = Wrapper.wrap_async_function_with_context(test_func, "dep", sample_class)
        
        # Проверяем что functools.wraps сохранил метаданные
        assert wrapped_func.__name__ == "test_async_function"
        assert wrapped_func.__module__ == "test_module"
        assert wrapped_func.__doc__ == "Test async function docstring."
