#!/usr/bin/env python3
"""
Пример использования Unit of Work с асинхронными генераторами в Skuf.

Этот пример демонстрирует:
1. Использование @asynccontextmanager для создания UoW
2. Регистрацию через async_generator_factory
3. Использование через AsyncGeneratorDependency
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from skuf import DIContainer, AsyncGeneratorDependency

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


class SQLAlchemyUnitOfWork(IUnitOfWork):
    """Реализация UoW для SQLAlchemy."""
    
    def __init__(self, session_factory):
        super().__init__()
        self.session_factory = session_factory
        self.session = None
    
    def __enter__(self):
        """Синхронный контекстный менеджер."""
        self.session = self.session_factory()
        logger.debug("SQLAlchemy сессия создана")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Выход из синхронного контекста."""
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        
        if self.session:
            self.session.close()
            logger.debug("SQLAlchemy сессия закрыта")
        return False


class SessionFactory:
    """Фабрика сессий SQLAlchemy."""
    
    def __init__(self):
        self.connection_count = 0
    
    def create_session(self):
        """Создать новую сессию."""
        self.connection_count += 1
        logger.debug(f"Создана сессия #{self.connection_count}")
        return f"Session-{self.connection_count}"


# Создаем фабрику сессий
session_factory = SessionFactory()


@asynccontextmanager
async def get_uow() -> AsyncGenerator[IUnitOfWork, None]:
    """
    Асинхронный контекстный менеджер для UoW.
    
    Этот декоратор создает асинхронный генератор, который:
    1. Создает UoW
    2. Логирует начало работы
    3. Возвращает UoW через yield
    4. Автоматически коммитит или откатывает транзакцию
    """
    logger.debug('🚀 UnitOfWork started')
    
    # Создаем UoW с сессией
    uow = SQLAlchemyUnitOfWork(session_factory)
    
    try:
        # Входим в синхронный контекст для инициализации сессии
        with uow:
            logger.debug('📝 UnitOfWork готов к работе')
            yield uow
            logger.debug('✅ UnitOfWork completed successfully')
    except Exception as e:
        logger.error(f'❌ UnitOfWork failed: {e}')
        raise
    finally:
        logger.debug('🔚 UnitOfWork cleanup completed')


async def business_logic_success():
    """Бизнес-логика с успешным выполнением."""
    print("\n=== Бизнес-логика с успешным выполнением ===")
    
    # Используем AsyncGeneratorDependency для получения UoW
    async for uow in AsyncGeneratorDependency(IUnitOfWork):
        uow.add_operation("Создать пользователя")
        uow.add_operation("Отправить email")
        uow.add_operation("Обновить статистику")
        # Все операции будут автоматически закоммичены


async def business_logic_with_error():
    """Бизнес-логика с ошибкой - демонстрация отката."""
    print("\n=== Бизнес-логика с ошибкой ===")
    
    try:
        async for uow in AsyncGeneratorDependency(IUnitOfWork):
            uow.add_operation("Создать пользователя")
            uow.add_operation("Отправить email")
            # Имитируем ошибку
            raise ValueError("Что-то пошло не так!")
    except ValueError as e:
        print(f"Поймано исключение: {e}")


async def multiple_operations():
    """Множественные операции в одном UoW."""
    print("\n=== Множественные операции ===")
    
    async for uow in AsyncGeneratorDependency(IUnitOfWork):
        # Группа операций 1
        uow.add_operation("Создать пользователя")
        uow.add_operation("Настроить профиль")
        
        # Группа операций 2
        uow.add_operation("Отправить приветственный email")
        uow.add_operation("Добавить в рассылку")
        
        # Группа операций 3
        uow.add_operation("Обновить статистику")
        uow.add_operation("Логировать активность")


async def main():
    """Основная функция для демонстрации."""
    print("🚀 Демонстрация Unit of Work с асинхронными генераторами в Skuf")
    
    # Регистрируем фабрику асинхронного генератора
    DIContainer.register(IUnitOfWork, async_generator_factory=get_uow)
    
    # Запускаем примеры
    await business_logic_success()
    await business_logic_with_error()
    await multiple_operations()
    
    print("\n✅ Демонстрация завершена!")


if __name__ == "__main__":
    asyncio.run(main())
