"""
Test configuration for dependency injection module.
"""
import pytest
from typing import Any, Dict, Type

from skuf.dependency.registry import DependencyRegistry


@pytest.fixture(autouse=True)
def clear_registry():
    """Automatically clears the dependency registry before each test."""
    DependencyRegistry.clear()
    yield
    DependencyRegistry.clear()


@pytest.fixture
def sample_class():
    """Simple class for testing."""
    class SampleClass:
        def __init__(self, value: str = "default"):
            self.value = value
            
        def get_value(self) -> str:
            return self.value
    
    return SampleClass


@pytest.fixture
def context_manager_class():
    """Class with context manager support for testing."""
    class ContextManagerClass:
        def __init__(self, value: str = "context"):
            self.value = value
            self.entered = False
            self.exited = False
            
        def __enter__(self):
            self.entered = True
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            self.exited = True
            return False
    
    return ContextManagerClass


@pytest.fixture
def async_context_manager_class():
    """Class with async context manager support for testing."""
    class AsyncContextManagerClass:
        def __init__(self, value: str = "async_context"):
            self.value = value
            self.entered = False
            self.exited = False
            
        async def __aenter__(self):
            self.entered = True
            return self
            
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            self.exited = True
            return False
    
    return AsyncContextManagerClass


@pytest.fixture
def async_generator_class():
    """Class with async generator support for testing."""
    class AsyncGeneratorClass:
        def __init__(self, value: str = "async_generator"):
            self.value = value
            
        def __aiter__(self):
            return self
            
        async def __anext__(self):
            if not hasattr(self, '_yielded'):
                self._yielded = True
                return self
            raise StopAsyncIteration
    
    return AsyncGeneratorClass
