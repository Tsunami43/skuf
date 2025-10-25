"""
Tests for inspector module.
"""
import pytest
from unittest.mock import Mock

from skuf.dependency.inspector import Inspector


class TestInspector:
    """Tests for Inspector class."""

    def test_is_context_manager_with_valid_context_manager(self):
        """Test context manager check with valid object."""
        # Create mock object with context manager methods
        obj = Mock()
        obj.__enter__ = Mock()
        obj.__exit__ = Mock()
        
        assert Inspector.is_context_manager(obj) is True

    def test_is_context_manager_without_enter(self):
        """Test context manager check without __enter__ method."""
        obj = Mock()
        obj.__exit__ = Mock()
        # Remove __enter__ method
        del obj.__enter__
        
        assert Inspector.is_context_manager(obj) is False

    def test_is_context_manager_without_exit(self):
        """Test context manager check without __exit__ method."""
        obj = Mock()
        obj.__enter__ = Mock()
        # Remove __exit__ method
        del obj.__exit__
        
        assert Inspector.is_context_manager(obj) is False

    def test_is_context_manager_with_regular_object(self):
        """Test context manager check with regular object."""
        obj = Mock()
        # Remove both context manager methods
        del obj.__enter__
        del obj.__exit__
        
        assert Inspector.is_context_manager(obj) is False

    def test_is_context_manager_with_none(self):
        """Test context manager check with None."""
        assert Inspector.is_context_manager(None) is False

    def test_is_async_context_manager_with_valid_async_context_manager(self):
        """Test async context manager check with valid object."""
        obj = Mock()
        obj.__aenter__ = Mock()
        obj.__aexit__ = Mock()
        
        assert Inspector.is_async_context_manager(obj) is True

    def test_is_async_context_manager_without_aenter(self):
        """Test async context manager check without __aenter__ method."""
        obj = Mock()
        obj.__aexit__ = Mock()
        # Remove __aenter__ method
        del obj.__aenter__
        
        assert Inspector.is_async_context_manager(obj) is False

    def test_is_async_context_manager_without_aexit(self):
        """Test async context manager check without __aexit__ method."""
        obj = Mock()
        obj.__aenter__ = Mock()
        # Remove __aexit__ method
        del obj.__aexit__
        
        assert Inspector.is_async_context_manager(obj) is False

    def test_is_async_context_manager_with_regular_object(self):
        """Test async context manager check with regular object."""
        obj = Mock()
        # Remove both async context manager methods
        del obj.__aenter__
        del obj.__aexit__
        
        assert Inspector.is_async_context_manager(obj) is False

    def test_is_async_context_manager_with_none(self):
        """Test async context manager check with None."""
        assert Inspector.is_async_context_manager(None) is False

    def test_is_async_generator_with_valid_async_generator(self):
        """Test async generator check with valid object."""
        obj = Mock()
        obj.__aiter__ = Mock()
        obj.__anext__ = Mock()
        
        assert Inspector.is_async_generator(obj) is True

    def test_is_async_generator_without_aiter(self):
        """Test async generator check without __aiter__ method."""
        obj = Mock()
        obj.__anext__ = Mock()
        # Remove __aiter__ method
        del obj.__aiter__
        
        assert Inspector.is_async_generator(obj) is False

    def test_is_async_generator_without_anext(self):
        """Test async generator check without __anext__ method."""
        obj = Mock()
        obj.__aiter__ = Mock()
        # Remove __anext__ method
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
