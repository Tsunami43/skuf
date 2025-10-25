"""
Factory Pattern Example - Dependency Creation with Factories
Demonstrates various factory patterns for creating dependencies.
"""
import asyncio
import random
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from skuf.dependency import Dependency


# Data Models
@dataclass
class User:
    id: str
    name: str
    email: str
    role: str
    created_at: datetime


@dataclass
class DatabaseConnection:
    host: str
    port: int
    database: str
    connected: bool = False
    
    def connect(self):
        self.connected = True
        print(f"🔌 Connected to {self.host}:{self.port}/{self.database}")
    
    def disconnect(self):
        self.connected = False
        print(f"🔌 Disconnected from {self.host}:{self.port}/{self.database}")


@dataclass
class CacheConnection:
    host: str
    port: int
    connected: bool = False
    
    def connect(self):
        self.connected = True
        print(f"📦 Connected to cache {self.host}:{self.port}")
    
    def disconnect(self):
        self.connected = False
        print(f"📦 Disconnected from cache {self.host}:{self.port}")


# Factory Functions
def create_database_connection() -> DatabaseConnection:
    """Factory for creating database connections"""
    # In real app, this would read from config
    return DatabaseConnection(
        host="localhost",
        port=5432,
        database="myapp"
    )


def create_cache_connection() -> CacheConnection:
    """Factory for creating cache connections"""
    return CacheConnection(
        host="localhost",
        port=6379
    )


def create_user_service() -> 'UserService':
    """Factory for creating UserService with dependencies"""
    # Get dependencies
    db = Dependency.resolve(DatabaseConnection)
    cache = Dependency.resolve(CacheConnection)
    logger = Dependency.resolve('Logger')
    
    return UserService(db, cache, logger)


def create_logger() -> 'Logger':
    """Factory for creating Logger with configuration"""
    return Logger("factory-example")


def create_email_service() -> 'EmailService':
    """Factory for creating EmailService with SMTP config"""
    return EmailService(
        smtp_host="smtp.gmail.com",
        smtp_port=587,
        username="app@example.com"
    )


def create_notification_service() -> 'NotificationService':
    """Factory for creating NotificationService with dependencies"""
    email_service = Dependency.resolve(EmailService)
    logger = Dependency.resolve('Logger')
    
    return NotificationService(email_service, logger)


# Services
class Logger:
    def __init__(self, name: str):
        self.name = name
    
    def info(self, message: str):
        print(f"[INFO] {self.name}: {message}")
    
    def error(self, message: str):
        print(f"[ERROR] {self.name}: {message}")


class EmailService:
    def __init__(self, smtp_host: str, smtp_port: int, username: str):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
    
    async def send_email(self, to: str, subject: str, body: str):
        print(f"📧 Sending email from {self.username} to {to}")
        print(f"   Subject: {subject}")
        print(f"   Body: {body}")
        await asyncio.sleep(0.1)  # Simulate email sending


class NotificationService:
    def __init__(self, email_service: EmailService, logger: Logger):
        self.email_service = email_service
        self.logger = logger
    
    async def send_welcome_email(self, user: User):
        self.logger.info(f"Sending welcome email to {user.email}")
        await self.email_service.send_email(
            to=user.email,
            subject="Welcome!",
            body=f"Hello {user.name}, welcome to our service!"
        )


class UserService:
    def __init__(self, db: DatabaseConnection, cache: CacheConnection, logger: Logger):
        self.db = db
        self.cache = cache
        self.logger = logger
    
    async def create_user(self, name: str, email: str, role: str = "user") -> User:
        self.logger.info(f"Creating user: {name}")
        
        # Connect to database
        self.db.connect()
        
        # Create user
        user = User(
            id=f"user-{random.randint(1000, 9999)}",
            name=name,
            email=email,
            role=role,
            created_at=datetime.now()
        )
        
        # Simulate database save
        print(f"💾 Saving user {user.id} to database")
        
        # Cache user data
        self.cache.connect()
        print(f"📦 Caching user {user.id}")
        
        self.logger.info(f"User {user.id} created successfully")
        return user
    
    async def get_user(self, user_id: str) -> Optional[User]:
        self.logger.info(f"Getting user: {user_id}")
        
        # Check cache first
        self.cache.connect()
        print(f"📦 Checking cache for user {user_id}")
        
        # If not in cache, check database
        self.db.connect()
        print(f"💾 Querying database for user {user_id}")
        
        # Simulate user found
        return User(
            id=user_id,
            name="Cached User",
            email="cached@example.com",
            role="user",
            created_at=datetime.now()
        )


# Setup Dependencies with Factories
def setup_dependencies():
    """Setup all dependencies using factory pattern"""
    
    # Register factories
    Dependency.register(DatabaseConnection, factory=create_database_connection)
    Dependency.register(CacheConnection, factory=create_cache_connection)
    Dependency.register('Logger', factory=create_logger)
    Dependency.register(EmailService, factory=create_email_service)
    Dependency.register(NotificationService, factory=create_notification_service)
    Dependency.register(UserService, factory=create_user_service)


# Main Application
async def main():
    """Main application demonstrating factory pattern"""
    print("🚀 Factory Pattern Example")
    
    # Setup dependencies
    setup_dependencies()
    
    # Get services (they will be created by factories)
    user_service = Dependency.resolve(UserService)
    notification_service = Dependency.resolve(NotificationService)
    
    # Create a user
    user = await user_service.create_user(
        name="Alice Johnson",
        email="alice@example.com",
        role="admin"
    )
    
    # Send welcome email
    await notification_service.send_welcome_email(user)
    
    # Get user (demonstrates caching)
    retrieved_user = await user_service.get_user(user.id)
    if retrieved_user:
        print(f"✅ Retrieved user: {retrieved_user.name}")
    
    print("🎉 Factory pattern example completed!")


if __name__ == "__main__":
    asyncio.run(main())
