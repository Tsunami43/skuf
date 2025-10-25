from typing import TypeVar, Generic

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)


class Dependency(Generic[T_co]):
    """
    Dependency marker class for type hints.
    Used in function signatures to indicate that a parameter should be injected.
    
    Example:
        def my_function(uow: Dependency[IUnitOfWork]):
            uow.add_operation("test")
    """
    pass


__all__ = ["T", "T_co", "Dependency"]
