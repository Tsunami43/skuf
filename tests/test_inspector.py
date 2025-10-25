"""
Тесты для модуля inspector.
"""
import pytest
from unittest.mock import Mock

from skuf.dependency.inspector import Inspector


class TestInspector:
    """Тесты для класса Inspector."""

    def test_is_context_manager_with_valid_context_manager(self):
        """Тест проверки context manager с валидным объектом."""
        # Создаем mock объект с методами context manager
        obj = Mock()
        obj.__enter__ = Mock()
        obj.__exit__ = Mock()
        
        assert Inspector.is_context_manager(obj) is True

    def test_is_context_manager_without_enter(self):
        """Тест проверки context manager без __enter__ метода."""
        obj = Mock()
        obj.__exit__ = Mock()
        # Удаляем __enter__ метод
        del obj.__enter__
        
        assert Inspector.is_context_manager(obj) is False

    def test_is_context_manager_without_exit(self):
        """Тест проверки context manager без __exit__ метода."""
        obj = Mock()
        obj.__enter__ = Mock()
        # Удаляем __exit__ метод
        del obj.__exit__
        
        assert Inspector.is_context_manager(obj) is False

    def test_is_context_manager_with_regular_object(self):
        """Тест проверки context manager с обычным объектом."""
        obj = Mock()
        # Удаляем оба метода context manager
        del obj.__enter__
        del obj.__exit__
        
        assert Inspector.is_context_manager(obj) is False

    def test_is_context_manager_with_none(self):
        """Тест проверки context manager с None."""
        assert Inspector.is_context_manager(None) is False

    def test_is_async_context_manager_with_valid_async_context_manager(self):
        """Тест проверки async context manager с валидным объектом."""
        obj = Mock()
        obj.__aenter__ = Mock()
        obj.__aexit__ = Mock()
        
        assert Inspector.is_async_context_manager(obj) is True

    def test_is_async_context_manager_without_aenter(self):
        """Тест проверки async context manager без __aenter__ метода."""
        obj = Mock()
        obj.__aexit__ = Mock()
        # Удаляем __aenter__ метод
        del obj.__aenter__
        
        assert Inspector.is_async_context_manager(obj) is False

    def test_is_async_context_manager_without_aexit(self):
        """Тест проверки async context manager без __aexit__ метода."""
        obj = Mock()
        obj.__aenter__ = Mock()
        # Удаляем __aexit__ метод
        del obj.__aexit__
        
        assert Inspector.is_async_context_manager(obj) is False

    def test_is_async_context_manager_with_regular_object(self):
        """Тест проверки async context manager с обычным объектом."""
        obj = Mock()
        # Удаляем оба метода async context manager
        del obj.__aenter__
        del obj.__aexit__
        
        assert Inspector.is_async_context_manager(obj) is False

    def test_is_async_context_manager_with_none(self):
        """Тест проверки async context manager с None."""
        assert Inspector.is_async_context_manager(None) is False

    def test_is_async_generator_with_valid_async_generator(self):
        """Тест проверки async generator с валидным объектом."""
        obj = Mock()
        obj.__aiter__ = Mock()
        obj.__anext__ = Mock()
        
        assert Inspector.is_async_generator(obj) is True

    def test_is_async_generator_without_aiter(self):
        """Тест проверки async generator без __aiter__ метода."""
        obj = Mock()
        obj.__anext__ = Mock()
        # Удаляем __aiter__ метод
        del obj.__aiter__
        
        assert Inspector.is_async_generator(obj) is False

    def test_is_async_generator_without_anext(self):
        """Тест проверки async generator без __anext__ метода."""
        obj = Mock()
        obj.__aiter__ = Mock()
        # Удаляем __anext__ метод
        del obj.__anext__
        
        assert Inspector.is_async_generator(obj) is False

    def test_is_async_generator_with_regular_object(self):
        """Тест проверки async generator с обычным объектом."""
        obj = Mock()
        # Удаляем оба метода async generator
        del obj.__aiter__
        del obj.__anext__
        
        assert Inspector.is_async_generator(obj) is False

    def test_is_async_generator_with_none(self):
        """Тест проверки async generator с None."""
        assert Inspector.is_async_generator(None) is False

    def test_real_context_manager(self):
        """Тест с реальным context manager."""
        class RealContextManager:
            def __enter__(self):
                return self
                
            def __exit__(self, exc_type, exc_val, exc_tb):
                pass
        
        obj = RealContextManager()
        assert Inspector.is_context_manager(obj) is True
        assert Inspector.is_async_context_manager(obj) is False
        assert Inspector.is_async_generator(obj) is False

    def test_real_async_context_manager(self):
        """Тест с реальным async context manager."""
        class RealAsyncContextManager:
            async def __aenter__(self):
                return self
                
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass
        
        obj = RealAsyncContextManager()
        assert Inspector.is_async_context_manager(obj) is True
        assert Inspector.is_context_manager(obj) is False
        assert Inspector.is_async_generator(obj) is False

    def test_real_async_generator(self):
        """Тест с реальным async generator."""
        class RealAsyncGenerator:
            def __aiter__(self):
                return self
                
            async def __anext__(self):
                raise StopAsyncIteration
        
        obj = RealAsyncGenerator()
        assert Inspector.is_async_generator(obj) is True
        assert Inspector.is_context_manager(obj) is False
        assert Inspector.is_async_context_manager(obj) is False
