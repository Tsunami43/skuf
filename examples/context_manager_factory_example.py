"""
Context Manager Factory Example - Resource Management
Demonstrates using factories to create context managers for resource management.
"""
import asyncio
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from contextlib import asynccontextmanager
from skuf.dependency import Dependency


# Data Models
@dataclass
class DatabaseSession:
    session_id: str
    connected: bool = False
    operations: List[str] = None
    
    def __post_init__(self):
        if self.operations is None:
            self.operations = []


@dataclass
class CacheSession:
    session_id: str
    connected: bool = False
    keys: List[str] = None
    
    def __post_init__(self):
        if self.keys is None:
            self.keys = []


# Context Managers
class DatabaseContextManager:
    def __init__(self, host: str, port: int, database: str):
        self.host = host
        self.port = port
        self.database = database
        self.session = None
    
    def __enter__(self):
        print(f"🔌 Connecting to database {self.host}:{self.port}/{self.database}")
        self.session = DatabaseSession(
            session_id=f"db-{datetime.now().timestamp()}"
        )
        self.session.connected = True
        return self.session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            print(f"✅ Committing database session {self.session.session_id}")
            print(f"   Operations: {self.session.operations}")
        else:
            print(f"❌ Rolling back database session {self.session.session_id}")
            print(f"   Error: {exc_val}")
        
        self.session.connected = False
        print(f"🔌 Disconnected from database")


class AsyncCacheContextManager:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.session = None
    
    async def __aenter__(self):
        print(f"📦 Connecting to cache {self.host}:{self.port}")
        await asyncio.sleep(0.1)  # Simulate connection delay
        self.session = CacheSession(
            session_id=f"cache-{datetime.now().timestamp()}"
        )
        self.session.connected = True
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            print(f"✅ Cache session {self.session.session_id} completed")
            print(f"   Keys accessed: {self.session.keys}")
        else:
            print(f"❌ Cache session {self.session.session_id} failed")
            print(f"   Error: {exc_val}")
        
        self.session.connected = False
        print(f"📦 Disconnected from cache")


@asynccontextmanager
async def get_database_session():
    """Async context manager factory for database sessions"""
    print("🚀 Starting database transaction")
    session = DatabaseSession(session_id=f"async-db-{datetime.now().timestamp()}")
    session.connected = True
    
    try:
        yield session
        print(f"✅ Database transaction committed: {session.operations}")
    except Exception as e:
        print(f"❌ Database transaction rolled back: {e}")
    finally:
        session.connected = False
        print("🔚 Database transaction ended")


# Factory Functions
def create_database_context_manager():
    """Factory for creating database context manager"""
    return DatabaseContextManager(
        host="localhost",
        port=5432,
        database="myapp"
    )


def create_cache_context_manager():
    """Factory for creating cache context manager"""
    return AsyncCacheContextManager(
        host="localhost",
        port=6379
    )


def create_async_database_session():
    """Factory for creating async database session"""
    return get_database_session()


# Services
class Logger:
    def __init__(self, name: str):
        self.name = name
    
    def info(self, message: str):
        print(f"[INFO] {self.name}: {message}")


class UserRepository:
    def __init__(self, logger: Logger):
        self.logger = logger
    
    def save_user(self, user_data: Dict[str, Any], db_session: DatabaseSession):
        self.logger.info(f"Saving user: {user_data['name']}")
        db_session.operations.append(f"INSERT user {user_data['name']}")
        print(f"💾 User {user_data['name']} saved to database")
    
    async def cache_user(self, user_data: Dict[str, Any], cache_session: CacheSession):
        self.logger.info(f"Caching user: {user_data['name']}")
        cache_session.keys.append(f"user:{user_data['id']}")
        print(f"📦 User {user_data['name']} cached")


class UserService:
    def __init__(self, repository: UserRepository, logger: Logger):
        self.repository = repository
        self.logger = logger
    
    def create_user(self, name: str, email: str, db_session: DatabaseSession):
        """Create user with database context manager"""
        user_data = {
            "id": f"user-{datetime.now().timestamp()}",
            "name": name,
            "email": email
        }
        
        self.repository.save_user(user_data, db_session)
        return user_data
    
    async def create_user_async(self, name: str, email: str, cache_session: CacheSession):
        """Create user with async cache context manager"""
        user_data = {
            "id": f"user-{datetime.now().timestamp()}",
            "name": name,
            "email": email
        }
        
        await self.repository.cache_user(user_data, cache_session)
        return user_data


# Setup Dependencies
def setup_dependencies():
    """Setup dependencies with context manager factories"""
    
    # Register context manager factories
    Dependency.register(DatabaseContextManager, factory=create_database_context_manager)
    Dependency.register(AsyncCacheContextManager, factory=create_cache_context_manager)
    Dependency.register('DatabaseSession', factory=create_async_database_session)
    
    # Register other services
    Dependency.register(Logger, instance=Logger("context-example"))
    
    @Dependency.inject
    def create_repository(logger: Dependency[Logger]):
        return UserRepository(logger)
    
    @Dependency.inject
    def create_user_service(repo: Dependency[UserRepository], logger: Dependency[Logger]):
        return UserService(repo, logger)
    
    Dependency.register(UserRepository, factory=create_repository)
    Dependency.register(UserService, factory=create_user_service)


# Main Application
async def main():
    """Main application demonstrating context manager factories"""
    print("🚀 Context Manager Factory Example")
    
    # Setup dependencies
    setup_dependencies()
    
    # Get services
    user_service = Dependency.resolve(UserService)
    
    # Example 1: Sync context manager
    print("\n=== Sync Context Manager Example ===")
    db_context = Dependency.resolve(DatabaseContextManager)
    
    with db_context as db_session:
        user = user_service.create_user("Alice Johnson", "alice@example.com", db_session)
        print(f"✅ Created user: {user['name']}")
    
    # Example 2: Async context manager
    print("\n=== Async Context Manager Example ===")
    cache_context = Dependency.resolve(AsyncCacheContextManager)
    
    async with cache_context as cache_session:
        user = await user_service.create_user_async("Bob Smith", "bob@example.com", cache_session)
        print(f"✅ Created user: {user['name']}")
    
    # Example 3: Async generator factory
    print("\n=== Async Generator Factory Example ===")
    async_db_session = Dependency.resolve('DatabaseSession')
    
    async with async_db_session as db_session:
        db_session.operations.append("SELECT * FROM users")
        db_session.operations.append("UPDATE users SET last_login = NOW()")
        print(f"✅ Database operations: {db_session.operations}")
    
    print("\n🎉 Context manager factory example completed!")


if __name__ == "__main__":
    asyncio.run(main())
