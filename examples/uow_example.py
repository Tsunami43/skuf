#!/usr/bin/env python3
"""
Пример использования Unit of Work (UoW) с контекстными менеджерами в Skuf.

Этот пример демонстрирует:
1. Создание UoW с контекстным менеджером
2. Создание асинхронного UoW
3. Регистрацию в DIContainer
4. Использование через ContextDependency и AsyncContextDependency
"""

import asyncio
from contextlib import contextmanager, asynccontextmanager
from typing import List, Optional
from skuf import DIContainer, ContextDependency, AsyncContextDependency


class Database:
    """Простая имитация базы данных."""
    
    def __init__(self):
        self.connected = False
        self.transaction_active = False
    
    def connect(self):
        print("🔌 Подключение к базе данных...")
        self.connected = True
    
    def disconnect(self):
        print("🔌 Отключение от базы данных...")
        self.connected = False
    
    def begin_transaction(self):
        print("🚀 Начало транзакции...")
        self.transaction_active = True
    
    def commit(self):
        print("✅ Коммит транзакции...")
        self.transaction_active = False
    
    def rollback(self):
        print("❌ Откат транзакции...")
        self.transaction_active = False


class UnitOfWork:
    """Unit of Work с контекстным менеджером."""
    
    def __init__(self, db: Database):
        self.db = db
        self.operations: List[str] = []
    
    def add_operation(self, operation: str):
        """Добавить операцию в UoW."""
        self.operations.append(operation)
        print(f"📝 Добавлена операция: {operation}")
    
    def __enter__(self):
        """Вход в контекст - начало транзакции."""
        self.db.begin_transaction()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Выход из контекста - коммит или откат."""
        if exc_type is None:
            # Нет исключений - коммитим
            self.db.commit()
            print(f"✅ Все операции выполнены: {self.operations}")
        else:
            # Есть исключение - откатываем
            self.db.rollback()
            print(f"❌ Откат операций: {self.operations}")
        return False  # Не подавляем исключения


class AsyncUnitOfWork:
    """Асинхронный Unit of Work с асинхронным контекстным менеджером."""
    
    def __init__(self, db: Database):
        self.db = db
        self.operations: List[str] = []
    
    def add_operation(self, operation: str):
        """Добавить операцию в UoW."""
        self.operations.append(operation)
        print(f"📝 Добавлена операция: {operation}")
    
    async def __aenter__(self):
        """Асинхронный вход в контекст - начало транзакции."""
        print("🚀 Асинхронное начало транзакции...")
        self.db.begin_transaction()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Асинхронный выход из контекста - коммит или откат."""
        if exc_type is None:
            # Нет исключений - коммитим
            self.db.commit()
            print(f"✅ Все асинхронные операции выполнены: {self.operations}")
        else:
            # Есть исключение - откатываем
            self.db.rollback()
            print(f"❌ Откат асинхронных операций: {self.operations}")
        return False  # Не подавляем исключения


def create_uow_context_manager() -> UnitOfWork:
    """Фабрика для создания UoW с контекстным менеджером."""
    db = Database()
    db.connect()
    return UnitOfWork(db)


def create_async_uow_context_manager() -> AsyncUnitOfWork:
    """Фабрика для создания асинхронного UoW с контекстным менеджером."""
    db = Database()
    db.connect()
    return AsyncUnitOfWork(db)


def sync_business_logic():
    """Синхронная бизнес-логика с использованием UoW."""
    print("\n=== Синхронная бизнес-логика ===")
    
    # Используем ContextDependency для получения UoW
    with ContextDependency(UnitOfWork) as uow:
        uow.add_operation("Создать пользователя")
        uow.add_operation("Отправить email")
        uow.add_operation("Обновить статистику")
        # Все операции будут закоммичены автоматически


def sync_business_logic_with_error():
    """Синхронная бизнес-логика с ошибкой - демонстрация отката."""
    print("\n=== Синхронная бизнес-логика с ошибкой ===")
    
    try:
        with ContextDependency(UnitOfWork) as uow:
            uow.add_operation("Создать пользователя")
            uow.add_operation("Отправить email")
            # Имитируем ошибку
            raise ValueError("Что-то пошло не так!")
    except ValueError as e:
        print(f"Поймано исключение: {e}")


async def async_business_logic():
    """Асинхронная бизнес-логика с использованием UoW."""
    print("\n=== Асинхронная бизнес-логика ===")
    
    # Используем AsyncContextDependency для получения UoW
    async with AsyncContextDependency(AsyncUnitOfWork) as uow:
        uow.add_operation("Асинхронно создать пользователя")
        uow.add_operation("Асинхронно отправить email")
        uow.add_operation("Асинхронно обновить статистику")
        # Все операции будут закоммичены автоматически


async def async_business_logic_with_error():
    """Асинхронная бизнес-логика с ошибкой - демонстрация отката."""
    print("\n=== Асинхронная бизнес-логика с ошибкой ===")
    
    try:
        async with AsyncContextDependency(AsyncUnitOfWork) as uow:
            uow.add_operation("Асинхронно создать пользователя")
            uow.add_operation("Асинхронно отправить email")
            # Имитируем ошибку
            raise ValueError("Асинхронная ошибка!")
    except ValueError as e:
        print(f"Поймано асинхронное исключение: {e}")


def main():
    """Основная функция для демонстрации."""
    print("🚀 Демонстрация Unit of Work с контекстными менеджерами в Skuf")
    
    # Регистрируем фабрики контекстных менеджеров
    DIContainer.register(UnitOfWork, context_manager=create_uow_context_manager)
    DIContainer.register(AsyncUnitOfWork, async_context_manager=create_async_uow_context_manager)
    
    # Синхронные примеры
    sync_business_logic()
    sync_business_logic_with_error()
    
    # Асинхронные примеры
    asyncio.run(async_business_logic())
    asyncio.run(async_business_logic_with_error())
    
    print("\n✅ Демонстрация завершена!")


if __name__ == "__main__":
    main()
