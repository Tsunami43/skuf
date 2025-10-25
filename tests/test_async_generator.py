import asyncio
from unittest import TestCase
from typing import AsyncGenerator

from skuf import DIContainer, AsyncGeneratorDependency


class TestAsyncGenerator(TestCase):
    """Тесты для асинхронных генераторов в DIContainer."""

    def setUp(self):
        """Очистка контейнера перед каждым тестом."""
        DIContainer.clear()

    def tearDown(self):
        """Очистка контейнера после каждого теста."""
        DIContainer.clear()

    def test_register_async_generator(self):
        """Тест регистрации асинхронного генератора."""
        class MockResource:
            def __init__(self):
                self.initialized = False
                self.cleaned_up = False

        async def create_async_generator() -> AsyncGenerator[MockResource, None]:
            resource = MockResource()
            resource.initialized = True
            try:
                yield resource
            finally:
                resource.cleaned_up = True

        # Регистрируем асинхронный генератор
        DIContainer.register(MockResource, async_generator_factory=create_async_generator)

        async def test_async_generator():
            async for resource in AsyncGeneratorDependency(MockResource):
                self.assertTrue(resource.initialized)
                self.assertFalse(resource.cleaned_up)

            # Проверяем, что ресурс был очищен
            self.assertTrue(resource.cleaned_up)

        # Запускаем асинхронный тест
        asyncio.run(test_async_generator())

    def test_async_generator_with_exception(self):
        """Тест асинхронного генератора с исключением."""
        class MockResource:
            def __init__(self):
                self.initialized = False
                self.cleaned_up = False
                self.exception_handled = False

        async def create_async_generator() -> AsyncGenerator[MockResource, None]:
            resource = MockResource()
            resource.initialized = True
            try:
                yield resource
            except Exception:
                resource.exception_handled = True
                raise
            finally:
                resource.cleaned_up = True

        DIContainer.register(MockResource, async_generator_factory=create_async_generator)

        async def test_async_generator_with_exception():
            with self.assertRaises(ValueError):
                async for resource in AsyncGeneratorDependency(MockResource):
                    self.assertTrue(resource.initialized)
                    raise ValueError("Тестовое исключение")

            # Проверяем, что ресурс был очищен и исключение обработано
            self.assertTrue(resource.cleaned_up)
            self.assertTrue(resource.exception_handled)

        # Запускаем асинхронный тест
        asyncio.run(test_async_generator_with_exception())

    def test_priority_order_with_async_generator(self):
        """Тест приоритета регистрации с асинхронным генератором."""
        class MockResource:
            def __init__(self, value):
                self.value = value

        def regular_factory():
            return MockResource("regular")

        def context_factory():
            return MockResource("context")

        async def async_generator_factory() -> AsyncGenerator[MockResource, None]:
            yield MockResource("async_generator")

        instance = MockResource("instance")

        # Тест 1: instance имеет приоритет над async_generator_factory
        DIContainer.register(
            MockResource,
            instance=instance,
            async_generator_factory=async_generator_factory
        )
        
        # Для instance используем обычный Dependency
        from skuf import Dependency
        resource = Dependency(MockResource)
        self.assertEqual(resource.value, "instance")

        DIContainer.clear()

        # Тест 2: factory имеет приоритет над async_generator_factory
        DIContainer.register(
            MockResource,
            factory=regular_factory,
            async_generator_factory=async_generator_factory
        )
        
        resource = Dependency(MockResource)
        self.assertEqual(resource.value, "regular")

        DIContainer.clear()

        # Тест 3: context_manager имеет приоритет над async_generator_factory
        DIContainer.register(
            MockResource,
            context_manager=context_factory,
            async_generator_factory=async_generator_factory
        )
        
        from skuf import ContextDependency
        with ContextDependency(MockResource) as resource:
            self.assertEqual(resource.value, "context")

    def test_unregistered_async_generator_raises_error(self):
        """Тест ошибки при попытке получить незарегистрированную зависимость."""
        class UnregisteredResource:
            pass

        with self.assertRaises(ValueError):
            AsyncGeneratorDependency(UnregisteredResource)

    def test_async_generator_factory_not_callable(self):
        """Тест ошибки при неправильной регистрации асинхронного генератора."""
        class MockResource:
            pass

        # Регистрируем неправильный тип
        DIContainer.register(MockResource, async_generator_factory="not_callable")

        with self.assertRaises(TypeError):
            AsyncGeneratorDependency(MockResource)

    def test_multiple_yields_in_async_generator(self):
        """Тест асинхронного генератора с множественными yield."""
        class MockResource:
            def __init__(self, value):
                self.value = value

        async def create_multiple_resources() -> AsyncGenerator[MockResource, None]:
            yield MockResource("first")
            yield MockResource("second")
            yield MockResource("third")

        DIContainer.register(MockResource, async_generator_factory=create_multiple_resources)

        async def test_multiple_yields():
            results = []
            async for resource in AsyncGeneratorDependency(MockResource):
                results.append(resource.value)

            self.assertEqual(len(results), 3)
            self.assertEqual(results, ["first", "second", "third"])

        # Запускаем асинхронный тест
        asyncio.run(test_multiple_yields())

    def test_async_generator_with_context_manager(self):
        """Тест комбинации асинхронного генератора с контекстным менеджером."""
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

        async def create_async_generator() -> AsyncGenerator[MockResource, None]:
            resource = MockResource()
            with resource:
                yield resource

        DIContainer.register(MockResource, async_generator_factory=create_async_generator)

        async def test_async_generator_with_context():
            async for resource in AsyncGeneratorDependency(MockResource):
                self.assertTrue(resource.initialized)
                self.assertFalse(resource.cleaned_up)

            # Проверяем, что ресурс был очищен
            self.assertTrue(resource.cleaned_up)

        # Запускаем асинхронный тест
        asyncio.run(test_async_generator_with_context())
