import asyncio
from contextlib import contextmanager, asynccontextmanager
from unittest import TestCase

from skuf import Dependency


class TestContextManagers(TestCase):
    """Тесты для контекстных менеджеров в DIContainer."""

    def setUp(self):
        """Очистка контейнера перед каждым тестом."""
        Dependency.clear()

    def tearDown(self):
        """Очистка контейнера после каждого теста."""
        Dependency.clear()

    def test_register_context_manager(self):
        """Тест регистрации контекстного менеджера."""
        class MockResource:
            def __init__(self):
                self.initialized = False
                self.cleaned_up = False

            def __enter__(self):
                self.initialized = True
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                self.cleaned_up = True
                return False

        def create_resource():
            return MockResource()

        # Регистрируем контекстный менеджер
        Dependency.register(MockResource, context_manager=create_resource)

        # Проверяем, что можем получить контекстный менеджер
        @Dependency.inject
        def test_function(resource: Dependency[MockResource]):
            self.assertTrue(resource.initialized)
            self.assertFalse(resource.cleaned_up)
            return resource

        resource = test_function()
        # Проверяем, что ресурс был очищен
        self.assertTrue(resource.cleaned_up)

    def test_register_async_context_manager(self):
        """Тест регистрации асинхронного контекстного менеджера."""
        class MockAsyncResource:
            def __init__(self):
                self.initialized = False
                self.cleaned_up = False

            async def __aenter__(self):
                self.initialized = True
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                self.cleaned_up = True
                return False

        def create_async_resource():
            return MockAsyncResource()

        # Регистрируем асинхронный контекстный менеджер
        Dependency.register(MockAsyncResource, async_context_manager=create_async_resource)

        async def test_async_context():
            async with AsyncContextDependency(MockAsyncResource) as resource:
                self.assertTrue(resource.initialized)
                self.assertFalse(resource.cleaned_up)

            # Проверяем, что ресурс был очищен
            self.assertTrue(resource.cleaned_up)

        # Запускаем асинхронный тест
        asyncio.run(test_async_context())

    def test_context_manager_with_exception(self):
        """Тест контекстного менеджера с исключением."""
        class MockResource:
            def __init__(self):
                self.initialized = False
                self.cleaned_up = False
                self.exception_handled = False

            def __enter__(self):
                self.initialized = True
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                self.cleaned_up = True
                if exc_type is not None:
                    self.exception_handled = True
                return False

        def create_resource():
            return MockResource()

        Dependency.register(MockResource, context_manager=create_resource)

        # Тест с исключением
        with self.assertRaises(ValueError):
            with ContextDependency(MockResource) as resource:
                self.assertTrue(resource.initialized)
                raise ValueError("Тестовое исключение")

        # Проверяем, что ресурс был очищен и исключение обработано
        self.assertTrue(resource.cleaned_up)
        self.assertTrue(resource.exception_handled)

    def test_async_context_manager_with_exception(self):
        """Тест асинхронного контекстного менеджера с исключением."""
        class MockAsyncResource:
            def __init__(self):
                self.initialized = False
                self.cleaned_up = False
                self.exception_handled = False

            async def __aenter__(self):
                self.initialized = True
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                self.cleaned_up = True
                if exc_type is not None:
                    self.exception_handled = True
                return False

        def create_async_resource():
            return MockAsyncResource()

        Dependency.register(MockAsyncResource, async_context_manager=create_async_resource)

        async def test_async_context_with_exception():
            with self.assertRaises(ValueError):
                async with AsyncContextDependency(MockAsyncResource) as resource:
                    self.assertTrue(resource.initialized)
                    raise ValueError("Асинхронное тестовое исключение")

            # Проверяем, что ресурс был очищен и исключение обработано
            self.assertTrue(resource.cleaned_up)
            self.assertTrue(resource.exception_handled)

        # Запускаем асинхронный тест
        asyncio.run(test_async_context_with_exception())

    def test_priority_order(self):
        """Тест приоритета регистрации зависимостей."""
        class MockResource:
            def __init__(self, value):
                self.value = value

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                return False

        # Создаем разные фабрики
        def context_factory():
            return MockResource("context")

        def async_context_factory():
            return MockResource("async_context")

        def regular_factory():
            return MockResource("regular")

        instance = MockResource("instance")

        # Тест 1: instance имеет приоритет над context_manager
        Dependency.register(
            MockResource,
            instance=instance,
            context_manager=context_factory
        )
        with ContextDependency(MockResource) as resource:
            self.assertEqual(resource.value, "instance")

        DIContainer.clear()

        # Тест 2: factory имеет приоритет над context_manager
        Dependency.register(
            MockResource,
            factory=regular_factory,
            context_manager=context_factory
        )
        with ContextDependency(MockResource) as resource:
            self.assertEqual(resource.value, "regular")

        DIContainer.clear()

        # Тест 3: context_manager имеет приоритет над async_context_manager
        Dependency.register(
            MockResource,
            context_manager=context_factory,
            async_context_manager=async_context_factory
        )
        with ContextDependency(MockResource) as resource:
            self.assertEqual(resource.value, "context")

    def test_unregistered_dependency_raises_error(self):
        """Тест ошибки при попытке получить незарегистрированную зависимость."""
        class UnregisteredResource:
            pass

        with self.assertRaises(ValueError):
            ContextDependency(UnregisteredResource)

        with self.assertRaises(ValueError):
            AsyncContextDependency(UnregisteredResource)

    def test_context_manager_factory_not_callable(self):
        """Тест ошибки при неправильной регистрации контекстного менеджера."""
        class MockResource:
            pass

        # Регистрируем неправильный тип
        Dependency.register(MockResource, context_manager="not_callable")

        with self.assertRaises(TypeError):
            ContextDependency(MockResource)

    def test_async_context_manager_factory_not_callable(self):
        """Тест ошибки при неправильной регистрации асинхронного контекстного менеджера."""
        class MockAsyncResource:
            pass

        # Регистрируем неправильный тип
        Dependency.register(MockAsyncResource, async_context_manager="not_callable")

        with self.assertRaises(TypeError):
            AsyncContextDependency(MockAsyncResource)
