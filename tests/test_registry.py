"""
Тесты для модуля registry.
"""
import pytest
import warnings
from unittest.mock import Mock, patch
from typing import ContextManager, AsyncContextManager, AsyncGenerator

from skuf.dependency.registry import DependencyRegistry


class TestDependencyRegistry:
    """Тесты для класса DependencyRegistry."""

    def test_register_with_instance(self, sample_class):
        """Тест регистрации зависимости с конкретным экземпляром."""
        instance = sample_class("test_value")
        DependencyRegistry.register(sample_class, instance=instance)
        
        resolved = DependencyRegistry.resolve(sample_class)
        assert resolved is instance
        assert resolved.value == "test_value"

    def test_register_with_factory(self, sample_class):
        """Тест регистрации зависимости с фабрикой."""
        def factory():
            return sample_class("factory_value")
        
        DependencyRegistry.register(sample_class, factory=factory)
        
        resolved = DependencyRegistry.resolve(sample_class)
        assert resolved.value == "factory_value"
        # Каждый вызов должен создавать новый экземпляр
        resolved2 = DependencyRegistry.resolve(sample_class)
        assert resolved is not resolved2
        assert resolved.value == resolved2.value

    def test_register_with_context_manager(self, context_manager_class):
        """Тест регистрации зависимости с context manager."""
        def context_factory():
            return context_manager_class("context_value")
        
        DependencyRegistry.register(context_manager_class, context_manager=context_factory)
        
        resolved = DependencyRegistry.resolve(context_manager_class)
        assert isinstance(resolved, context_manager_class)
        assert resolved.value == "context_value"

    def test_register_with_async_context_manager(self, async_context_manager_class):
        """Тест регистрации зависимости с async context manager."""
        def async_context_factory():
            return async_context_manager_class("async_context_value")
        
        DependencyRegistry.register(async_context_manager_class, async_context_manager=async_context_factory)
        
        resolved = DependencyRegistry.resolve(async_context_manager_class)
        assert isinstance(resolved, async_context_manager_class)
        assert resolved.value == "async_context_value"

    def test_register_with_async_generator_factory(self, async_generator_class):
        """Тест регистрации зависимости с async generator factory."""
        def async_generator_factory():
            return async_generator_class("async_generator_value")
        
        DependencyRegistry.register(async_generator_class, async_generator_factory=async_generator_factory)
        
        resolved = DependencyRegistry.resolve(async_generator_class)
        assert isinstance(resolved, async_generator_class)
        assert resolved.value == "async_generator_value"

    def test_register_with_default_constructor(self, sample_class):
        """Тест регистрации зависимости с конструктором по умолчанию."""
        DependencyRegistry.register(sample_class)
        
        resolved = DependencyRegistry.resolve(sample_class)
        assert isinstance(resolved, sample_class)
        assert resolved.value == "default"

    def test_register_priority_instance_over_factory(self, sample_class):
        """Тест приоритета instance над factory."""
        instance = sample_class("instance_value")
        factory_instance = sample_class("factory_value")
        
        def factory():
            return factory_instance
        
        DependencyRegistry.register(sample_class, instance=instance, factory=factory)
        
        resolved = DependencyRegistry.resolve(sample_class)
        assert resolved is instance
        assert resolved.value == "instance_value"

    def test_register_priority_factory_over_context_manager(self, sample_class):
        """Тест приоритета factory над context_manager."""
        factory_instance = sample_class("factory_value")
        context_instance = sample_class("context_value")
        
        def factory():
            return factory_instance
            
        def context_factory():
            return context_instance
        
        DependencyRegistry.register(
            sample_class, 
            factory=factory, 
            context_manager=context_factory
        )
        
        resolved = DependencyRegistry.resolve(sample_class)
        assert resolved is factory_instance
        assert resolved.value == "factory_value"

    def test_resolve_unregistered_dependency(self, sample_class):
        """Тест разрешения незарегистрированной зависимости."""
        with pytest.raises(ValueError, match="Dependency .* is not registered"):
            DependencyRegistry.resolve(sample_class)

    def test_resolve_with_factory_creates_new_instance(self, sample_class):
        """Тест что factory создает новый экземпляр при каждом вызове."""
        def factory():
            return sample_class("factory_value")
        
        DependencyRegistry.register(sample_class, factory=factory)
        
        resolved1 = DependencyRegistry.resolve(sample_class)
        resolved2 = DependencyRegistry.resolve(sample_class)
        
        assert resolved1 is not resolved2
        assert resolved1.value == resolved2.value

    def test_clear_registry(self, sample_class):
        """Тест очистки реестра."""
        instance = sample_class("test_value")
        DependencyRegistry.register(sample_class, instance=instance)
        
        # Проверяем что зависимость зарегистрирована
        resolved = DependencyRegistry.resolve(sample_class)
        assert resolved is instance
        
        # Очищаем реестр
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            DependencyRegistry.clear()
            assert len(w) == 1
            assert issubclass(w[0].category, UserWarning)
            assert "Clearing the registry" in str(w[0].message)
        
        # Проверяем что зависимость больше не зарегистрирована
        with pytest.raises(ValueError, match="Dependency .* is not registered"):
            DependencyRegistry.resolve(sample_class)

    def test_register_multiple_dependencies(self, sample_class, context_manager_class):
        """Тест регистрации нескольких зависимостей."""
        instance1 = sample_class("value1")
        instance2 = context_manager_class("value2")
        
        DependencyRegistry.register(sample_class, instance=instance1)
        DependencyRegistry.register(context_manager_class, instance=instance2)
        
        resolved1 = DependencyRegistry.resolve(sample_class)
        resolved2 = DependencyRegistry.resolve(context_manager_class)
        
        assert resolved1 is instance1
        assert resolved2 is instance2

    def test_register_overwrite_existing(self, sample_class):
        """Тест перезаписи существующей зависимости."""
        instance1 = sample_class("value1")
        instance2 = sample_class("value2")
        
        DependencyRegistry.register(sample_class, instance=instance1)
        resolved1 = DependencyRegistry.resolve(sample_class)
        assert resolved1 is instance1
        
        DependencyRegistry.register(sample_class, instance=instance2)
        resolved2 = DependencyRegistry.resolve(sample_class)
        assert resolved2 is instance2

    def test_factory_with_side_effects(self, sample_class):
        """Тест фабрики с побочными эффектами."""
        call_count = 0
        
        def factory():
            nonlocal call_count
            call_count += 1
            return sample_class(f"call_{call_count}")
        
        DependencyRegistry.register(sample_class, factory=factory)
        
        resolved1 = DependencyRegistry.resolve(sample_class)
        resolved2 = DependencyRegistry.resolve(sample_class)
        
        assert call_count == 2
        assert resolved1.value == "call_1"
        assert resolved2.value == "call_2"

    def test_context_manager_factory_returns_context_manager(self, context_manager_class):
        """Тест что context manager factory возвращает context manager."""
        def context_factory():
            return context_manager_class("test")
        
        DependencyRegistry.register(context_manager_class, context_manager=context_factory)
        
        resolved = DependencyRegistry.resolve(context_manager_class)
        assert hasattr(resolved, "__enter__")
        assert hasattr(resolved, "__exit__")

    def test_async_context_manager_factory_returns_async_context_manager(self, async_context_manager_class):
        """Тест что async context manager factory возвращает async context manager."""
        def async_context_factory():
            return async_context_manager_class("test")
        
        DependencyRegistry.register(async_context_manager_class, async_context_manager=async_context_factory)
        
        resolved = DependencyRegistry.resolve(async_context_manager_class)
        assert hasattr(resolved, "__aenter__")
        assert hasattr(resolved, "__aexit__")

    def test_async_generator_factory_returns_async_generator(self, async_generator_class):
        """Тест что async generator factory возвращает async generator."""
        def async_generator_factory():
            return async_generator_class("test")
        
        DependencyRegistry.register(async_generator_class, async_generator_factory=async_generator_factory)
        
        resolved = DependencyRegistry.resolve(async_generator_class)
        assert hasattr(resolved, "__aiter__")
        assert hasattr(resolved, "__anext__")
