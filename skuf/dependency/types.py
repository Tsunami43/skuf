from typing import TypeVar, AsyncContextManager, ContextManager, AsyncGenerator, Protocol, Type, Generic

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)


class ContextManagerFactory(Protocol[T_co]):
    def __call__(self) -> ContextManager[T_co]: ...


class AsyncContextManagerFactory(Protocol[T_co]):
    def __call__(self) -> AsyncContextManager[T_co]: ...


class AsyncGeneratorFactory(Protocol[T_co]):
    def __call__(self) -> AsyncGenerator[T_co, None]: ...


class Dependency(Generic[T_co]):
    """
    Dependency marker class for type hints.
    Used in function signatures to indicate that a parameter should be injected.
    
    Example:
        def my_function(uow: Dependency[IUnitOfWork]):
            uow.add_operation("test")
    """
    pass


__all__ = ["T", "T_co", "ContextManagerFactory", "AsyncContextManagerFactory", "AsyncGeneratorFactory", "Dependency"]
