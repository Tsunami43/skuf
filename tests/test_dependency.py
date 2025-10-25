"""
Тесты для основного модуля dependency.
"""
import pytest
from unittest.mock import Mock, patch

from skuf.dependency import Dependency
from skuf.dependency.registry import DependencyRegistry
from skuf.dependency.injector import Injector


class TestDependency:
    """Тесты для основного класса Dependency."""

    def test_register_delegates_to_registry(self, sample_class):
        """Тест что register делегирует вызов в DependencyRegistry."""
        instance = sample_class("test_value")
        
        with patch.object(DependencyRegistry, 'register') as mock_register:
            Dependency.register(sample_class, instance=instance)
            mock_register.assert_called_once_with(sample_class, instance=instance)

    def test_resolve_delegates_to_registry(self, sample_class):
        """Тест что resolve делегирует вызов в DependencyRegistry."""
        instance = sample_class("test_value")
        DependencyRegistry.register(sample_class, instance=instance)
        
        with patch.object(DependencyRegistry, 'resolve') as mock_resolve:
            mock_resolve.return_value = instance
            result = Dependency.resolve(sample_class)
            mock_resolve.assert_called_once_with(sample_class)
            assert result is instance

    def test_clear_delegates_to_registry(self):
        """Тест что clear делегирует вызов в DependencyRegistry."""
        with patch.object(DependencyRegistry, 'clear') as mock_clear:
            Dependency.clear()
            mock_clear.assert_called_once()

    def test_inject_delegates_to_injector(self, sample_class):
        """Тест что inject делегирует вызов в Injector."""
        def test_func(dep: Dependency[sample_class]):
            return dep.get_value()
        
        with patch.object(Injector, 'inject') as mock_inject:
            mock_inject.return_value = test_func
            result = Dependency.inject(test_func)
            mock_inject.assert_called_once_with(test_func)
            assert result is test_func

    def test_class_getitem_returns_dependency_type(self):
        """Тест что __class_getitem__ возвращает правильный тип."""
        from skuf.dependency.types import Dependency as DependencyType
        
        result = Dependency[str]
        assert result is DependencyType[str]

    def test_class_getitem_with_different_types(self):
        """Тест __class_getitem__ с различными типами."""
        from skuf.dependency.types import Dependency as DependencyType
        
        # Строка
        str_result = Dependency[str]
        assert str_result is DependencyType[str]
        
        # Число
        int_result = Dependency[int]
        assert int_result is DependencyType[int]
        
        # Пользовательский класс
        class CustomClass:
            pass
        
        custom_result = Dependency[CustomClass]
        assert custom_result is DependencyType[CustomClass]

    def test_register_with_factory(self, sample_class):
        """Тест регистрации с фабрикой через Dependency."""
        def factory():
            return sample_class("factory_value")
        
        Dependency.register(sample_class, factory=factory)
        
        resolved = Dependency.resolve(sample_class)
        assert resolved.value == "factory_value"

    def test_register_with_context_manager(self, context_manager_class):
        """Тест регистрации с context manager через Dependency."""
        def context_factory():
            return context_manager_class("context_value")
        
        Dependency.register(context_manager_class, context_manager=context_factory)
        
        resolved = Dependency.resolve(context_manager_class)
        assert resolved.value == "context_value"

    def test_register_with_async_context_manager(self, async_context_manager_class):
        """Тест регистрации с async context manager через Dependency."""
        def async_context_factory():
            return async_context_manager_class("async_context_value")
        
        Dependency.register(async_context_manager_class, async_context_manager=async_context_factory)
        
        resolved = Dependency.resolve(async_context_manager_class)
        assert resolved.value == "async_context_value"

    def test_register_with_async_generator_factory(self, async_generator_class):
        """Тест регистрации с async generator factory через Dependency."""
        def async_generator_factory():
            return async_generator_class("async_generator_value")
        
        Dependency.register(async_generator_class, async_generator_factory=async_generator_factory)
        
        resolved = Dependency.resolve(async_generator_class)
        assert resolved.value == "async_generator_value"

    def test_inject_decorator_usage(self, sample_class):
        """Тест использования inject как декоратора."""
        instance = sample_class("test_value")
        Dependency.register(sample_class, instance=instance)
        
        @Dependency.inject
        def test_func(dep: Dependency[sample_class]):
            return dep.get_value()
        
        result = test_func()
        assert result == "test_value"

    @pytest.mark.asyncio
    async def test_inject_decorator_with_async_function(self, sample_class):
        """Тест использования inject как декоратора с async функцией."""
        instance = sample_class("test_value")
        Dependency.register(sample_class, instance=instance)
        
        @Dependency.inject
        async def test_func(dep: Dependency[sample_class]):
            return dep.get_value()
        
        result = await test_func()
        assert result == "test_value"

    def test_inject_decorator_with_multiple_dependencies(self, sample_class, context_manager_class):
        """Тест inject декоратора с несколькими зависимостями."""
        instance1 = sample_class("value1")
        instance2 = context_manager_class("value2")
        
        Dependency.register(sample_class, instance=instance1)
        Dependency.register(context_manager_class, instance=instance2)
        
        @Dependency.inject
        def test_func(dep1: Dependency[sample_class], dep2: Dependency[context_manager_class]):
            return f"{dep1.get_value()}_{dep2.value}"
        
        result = test_func()
        assert result == "value1_value2"

    def test_inject_decorator_with_mixed_parameters(self, sample_class):
        """Тест inject декоратора со смешанными параметрами."""
        instance = sample_class("test_value")
        Dependency.register(sample_class, instance=instance)
        
        @Dependency.inject
        def test_func(regular_param: str, dep: Dependency[sample_class], another_regular: int):
            return f"{regular_param}_{dep.get_value()}_{another_regular}"
        
        result = test_func("hello", 42)
        assert result == "hello_test_value_42"

    def test_inject_decorator_preserves_function_metadata(self, sample_class):
        """Тест что inject декоратор сохраняет метаданные функции."""
        instance = sample_class("test_value")
        Dependency.register(sample_class, instance=instance)
        
        @Dependency.inject
        def test_func(dep: Dependency[sample_class]):
            """Test function docstring."""
            return dep.get_value()
        
        test_func.__name__ = "test_function"
        test_func.__module__ = "test_module"
        
        # Проверяем что метаданные сохранены
        assert test_func.__name__ == "test_function"
        assert test_func.__module__ == "test_module"
        assert test_func.__doc__ == "Test function docstring."

    def test_inject_decorator_with_unregistered_dependency_raises_error(self, sample_class):
        """Тест что inject декоратор с незарегистрированной зависимостью вызывает ошибку."""
        @Dependency.inject
        def test_func(dep: Dependency[sample_class]):
            return dep.get_value()
        
        with pytest.raises(ValueError, match="Dependency .* is not registered"):
            test_func()

    def test_clear_clears_all_dependencies(self, sample_class, context_manager_class):
        """Тест что clear очищает все зависимости."""
        instance1 = sample_class("value1")
        instance2 = context_manager_class("value2")
        
        Dependency.register(sample_class, instance=instance1)
        Dependency.register(context_manager_class, instance=instance2)
        
        # Проверяем что зависимости зарегистрированы
        resolved1 = Dependency.resolve(sample_class)
        resolved2 = Dependency.resolve(context_manager_class)
        assert resolved1 is instance1
        assert resolved2 is instance2
        
        # Очищаем реестр
        Dependency.clear()
        
        # Проверяем что зависимости больше не зарегистрированы
        with pytest.raises(ValueError, match="Dependency .* is not registered"):
            Dependency.resolve(sample_class)
        
        with pytest.raises(ValueError, match="Dependency .* is not registered"):
            Dependency.resolve(context_manager_class)

    def test_register_overwrite_existing(self, sample_class):
        """Тест перезаписи существующей зависимости."""
        instance1 = sample_class("value1")
        instance2 = sample_class("value2")
        
        Dependency.register(sample_class, instance=instance1)
        resolved1 = Dependency.resolve(sample_class)
        assert resolved1 is instance1
        
        Dependency.register(sample_class, instance=instance2)
        resolved2 = Dependency.resolve(sample_class)
        assert resolved2 is instance2

    def test_integration_test_full_workflow(self, sample_class):
        """Интеграционный тест полного рабочего процесса."""
        # Регистрируем зависимость
        instance = sample_class("integration_test")
        Dependency.register(sample_class, instance=instance)
        
        # Создаем функцию с инъекцией зависимостей
        @Dependency.inject
        def business_logic(dep: Dependency[sample_class]):
            return f"processed_{dep.get_value()}"
        
        # Вызываем функцию
        result = business_logic()
        assert result == "processed_integration_test"
        
        # Очищаем реестр
        Dependency.clear()
        
        # Проверяем что зависимость больше не доступна
        with pytest.raises(ValueError, match="Dependency .* is not registered"):
            business_logic()
