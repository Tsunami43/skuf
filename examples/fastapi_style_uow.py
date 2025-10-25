#!/usr/bin/env python3
"""
Пример использования Unit of Work в стиле FastAPI с автоматическим управлением контекстом.

Этот пример демонстрирует:
1. Упрощенный API без DIContainer
2. Автоматическое управление контекстом в рамках функции
3. Поддержку синхронных и асинхронных UoW
4. Использование декоратора @Dependency.inject
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from skuf import Dependency

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class IUnitOfWork:
    """Интерфейс Unit of Work."""
    
    def __init__(self):
        self.operations = []
        self.committed = False
        self.rolled_back = False
    
    def add_operation(self, operation: str):
        """Добавить операцию в UoW."""
        self.operations.append(operation)
        logger.debug(f"Добавлена операция: {operation}")
    
    def commit(self):
        """Зафиксировать транзакцию."""
        self.committed = True
        logger.debug(f"Транзакция зафиксирована: {self.operations}")
    
    def rollback(self):
        """Откатить транзакцию."""
        self.rolled_back = True
        logger.debug(f"Транзакция откачена: {self.operations}")


class UnitOfWork(IUnitOfWork):
    """Синхронный Unit of Work с контекстным менеджером."""
    
    def __enter__(self):
        logger.debug("🚀 Синхронный UnitOfWork начат")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.commit()
            logger.debug("✅ Синхронный UnitOfWork завершен успешно")
        else:
            self.rollback()
            logger.debug("❌ Синхронный UnitOfWork откачен")
        return False


class AsyncUnitOfWork(IUnitOfWork):
    """Асинхронный Unit of Work с контекстным менеджером."""
    
    async def __aenter__(self):
        logger.debug("🚀 Асинхронный UnitOfWork начат")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.commit()
            logger.debug("✅ Асинхронный UnitOfWork завершен успешно")
        else:
            self.rollback()
            logger.debug("❌ Асинхронный UnitOfWork откачен")
        return False


@asynccontextmanager
async def get_async_uow() -> AsyncGenerator[IUnitOfWork, None]:
    """
    Асинхронный генератор для UoW.
    
    Этот декоратор создает асинхронный генератор, который:
    1. Создает UoW
    2. Логирует начало работы
    3. Возвращает UoW через yield
    4. Автоматически коммитит или откатывает транзакцию
    """
    logger.debug('🚀 AsyncGenerator UnitOfWork started')
    
    uow = AsyncUnitOfWork()
    
    try:
        async with uow:
            logger.debug('📝 AsyncGenerator UnitOfWork готов к работе')
            yield uow
            logger.debug('✅ AsyncGenerator UnitOfWork completed successfully')
    except Exception as e:
        logger.error(f'❌ AsyncGenerator UnitOfWork failed: {e}')
        raise
    finally:
        logger.debug('🔚 AsyncGenerator UnitOfWork cleanup completed')


def create_sync_uow() -> UnitOfWork:
    """Фабрика для синхронного UoW."""
    return UnitOfWork()


def create_async_uow() -> AsyncUnitOfWork:
    """Фабрика для асинхронного UoW."""
    return AsyncUnitOfWork()


# Регистрируем зависимости
Dependency.register(UnitOfWork, context_manager=create_sync_uow)
Dependency.register(AsyncUnitOfWork, async_context_manager=create_async_uow)
Dependency.register(IUnitOfWork, async_generator_factory=get_async_uow)


# Синхронные функции с автоматическим управлением контекстом
@Dependency.inject
def sync_business_logic(uow: Dependency[UnitOfWork]):
    """Синхронная бизнес-логика с автоматическим управлением контекстом."""
    print("\n=== Синхронная бизнес-логика ===")
    uow.add_operation("Создать пользователя")
    uow.add_operation("Отправить email")
    uow.add_operation("Обновить статистику")
    # Контекст автоматически управляется декоратором


@Dependency.inject
def sync_business_logic_with_error(uow: Dependency[UnitOfWork]):
    """Синхронная бизнес-логика с ошибкой."""
    print("\n=== Синхронная бизнес-логика с ошибкой ===")
    uow.add_operation("Создать пользователя")
    uow.add_operation("Отправить email")
    # Имитируем ошибку
    raise ValueError("Что-то пошло не так!")


# Асинхронные функции с автоматическим управлением контекстом
@Dependency.inject
async def async_business_logic(uow: Dependency[AsyncUnitOfWork]):
    """Асинхронная бизнес-логика с автоматическим управлением контекстом."""
    print("\n=== Асинхронная бизнес-логика ===")
    uow.add_operation("Асинхронно создать пользователя")
    uow.add_operation("Асинхронно отправить email")
    uow.add_operation("Асинхронно обновить статистику")
    # Контекст автоматически управляется декоратором


@Dependency.inject
async def async_business_logic_with_error(uow: Dependency[AsyncUnitOfWork]):
    """Асинхронная бизнес-логика с ошибкой."""
    print("\n=== Асинхронная бизнес-логика с ошибкой ===")
    uow.add_operation("Асинхронно создать пользователя")
    uow.add_operation("Асинхронно отправить email")
    # Имитируем ошибку
    raise ValueError("Асинхронная ошибка!")


# Асинхронные функции с генератором
@Dependency.inject
async def async_generator_business_logic(uow: Dependency[IUnitOfWork]):
    """Асинхронная бизнес-логика с генератором."""
    print("\n=== Асинхронная бизнес-логика с генератором ===")
    uow.add_operation("Генератор: создать пользователя")
    uow.add_operation("Генератор: отправить email")
    uow.add_operation("Генератор: обновить статистику")
    # Контекст автоматически управляется декоратором


@Dependency.inject
async def async_generator_business_logic_with_error(uow: Dependency[IUnitOfWork]):
    """Асинхронная бизнес-логика с генератором и ошибкой."""
    print("\n=== Асинхронная бизнес-логика с генератором и ошибкой ===")
    uow.add_operation("Генератор: создать пользователя")
    uow.add_operation("Генератор: отправить email")
    # Имитируем ошибку
    raise ValueError("Ошибка в генераторе!")


async def main():
    """Основная функция для демонстрации."""
    print("🚀 Демонстрация Unit of Work в стиле FastAPI с автоматическим управлением контекстом")
    
    # Синхронные примеры
    try:
        sync_business_logic()
    except Exception as e:
        print(f"Поймано синхронное исключение: {e}")
    
    try:
        sync_business_logic_with_error()
    except Exception as e:
        print(f"Поймано синхронное исключение: {e}")
    
    # Асинхронные примеры
    try:
        await async_business_logic()
    except Exception as e:
        print(f"Поймано асинхронное исключение: {e}")
    
    try:
        await async_business_logic_with_error()
    except Exception as e:
        print(f"Поймано асинхронное исключение: {e}")
    
    # Асинхронные примеры с генератором
    try:
        await async_generator_business_logic()
    except Exception as e:
        print(f"Поймано исключение в генераторе: {e}")
    
    try:
        await async_generator_business_logic_with_error()
    except Exception as e:
        print(f"Поймано исключение в генераторе: {e}")
    
    print("\n✅ Демонстрация завершена!")


if __name__ == "__main__":
    asyncio.run(main())
