"""
Configuration Factory Example - Environment-based Configuration
Demonstrates using factories to create services based on configuration.
"""
import os
import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from skuf.dependency import Dependency


# Configuration Models
class Environment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class DatabaseConfig:
    host: str
    port: int
    database: str
    username: str
    password: str
    ssl: bool = False


@dataclass
class CacheConfig:
    host: str
    port: int
    password: Optional[str] = None
    ssl: bool = False


@dataclass
class EmailConfig:
    smtp_host: str
    smtp_port: int
    username: str
    password: str
    ssl: bool = True


# Services
class DatabaseService:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.connected = False
    
    def connect(self):
        ssl_info = " with SSL" if self.config.ssl else ""
        print(f"🔌 Connecting to {self.config.host}:{self.config.port}/{self.config.database}{ssl_info}")
        self.connected = True
    
    def disconnect(self):
        print(f"🔌 Disconnected from {self.config.host}:{self.config.port}")
        self.connected = False


class CacheService:
    def __init__(self, config: CacheConfig):
        self.config = config
        self.connected = False
    
    def connect(self):
        ssl_info = " with SSL" if self.config.ssl else ""
        print(f"📦 Connecting to cache {self.config.host}:{self.config.port}{ssl_info}")
        self.connected = True
    
    def disconnect(self):
        print(f"📦 Disconnected from cache {self.config.host}:{self.config.port}")
        self.connected = False


class EmailService:
    def __init__(self, config: EmailConfig):
        self.config = config
    
    async def send_email(self, to: str, subject: str, body: str):
        ssl_info = " with SSL" if self.config.ssl else ""
        print(f"📧 Sending email via {self.config.smtp_host}:{self.config.smtp_port}{ssl_info}")
        print(f"   From: {self.config.username}")
        print(f"   To: {to}")
        print(f"   Subject: {subject}")
        await asyncio.sleep(0.1)  # Simulate email sending


class Logger:
    def __init__(self, name: str, level: str = "INFO"):
        self.name = name
        self.level = level
    
    def info(self, message: str):
        if self.level in ["INFO", "DEBUG"]:
            print(f"[INFO] {self.name}: {message}")
    
    def debug(self, message: str):
        if self.level == "DEBUG":
            print(f"[DEBUG] {self.name}: {message}")


class ApplicationService:
    def __init__(self, db: DatabaseService, cache: CacheService, email: EmailService, logger: Logger):
        self.db = db
        self.cache = cache
        self.email = email
        self.logger = logger
    
    async def process_user_registration(self, name: str, email: str):
        self.logger.info(f"Processing registration for {name}")
        
        # Connect to services
        self.db.connect()
        self.cache.connect()
        
        # Simulate processing
        print(f"💾 Saving user {name} to database")
        print(f"📦 Caching user data for {name}")
        
        # Send welcome email
        await self.email.send_email(
            to=email,
            subject="Welcome!",
            body=f"Hello {name}, welcome to our service!"
        )
        
        self.logger.info(f"Registration completed for {name}")


# Configuration Factory Functions
def get_environment() -> Environment:
    """Get current environment from environment variable"""
    env_str = os.getenv("APP_ENV", "development").lower()
    try:
        return Environment(env_str)
    except ValueError:
        return Environment.DEVELOPMENT


def create_database_config() -> DatabaseConfig:
    """Create database configuration based on environment"""
    env = get_environment()
    
    if env == Environment.PRODUCTION:
        return DatabaseConfig(
            host=os.getenv("DB_HOST", "prod-db.example.com"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "myapp_prod"),
            username=os.getenv("DB_USER", "prod_user"),
            password=os.getenv("DB_PASSWORD", "secure_password"),
            ssl=True
        )
    elif env == Environment.STAGING:
        return DatabaseConfig(
            host=os.getenv("DB_HOST", "staging-db.example.com"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "myapp_staging"),
            username=os.getenv("DB_USER", "staging_user"),
            password=os.getenv("DB_PASSWORD", "staging_password"),
            ssl=True
        )
    else:  # DEVELOPMENT
        return DatabaseConfig(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "myapp_dev"),
            username=os.getenv("DB_USER", "dev_user"),
            password=os.getenv("DB_PASSWORD", "dev_password"),
            ssl=False
        )


def create_cache_config() -> CacheConfig:
    """Create cache configuration based on environment"""
    env = get_environment()
    
    if env == Environment.PRODUCTION:
        return CacheConfig(
            host=os.getenv("CACHE_HOST", "prod-cache.example.com"),
            port=int(os.getenv("CACHE_PORT", "6379")),
            password=os.getenv("CACHE_PASSWORD", "secure_cache_password"),
            ssl=True
        )
    else:  # DEVELOPMENT/STAGING
        return CacheConfig(
            host=os.getenv("CACHE_HOST", "localhost"),
            port=int(os.getenv("CACHE_PORT", "6379")),
            password=os.getenv("CACHE_PASSWORD"),
            ssl=False
        )


def create_email_config() -> EmailConfig:
    """Create email configuration based on environment"""
    env = get_environment()
    
    if env == Environment.PRODUCTION:
        return EmailConfig(
            smtp_host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            username=os.getenv("SMTP_USER", "noreply@myapp.com"),
            password=os.getenv("SMTP_PASSWORD", "secure_email_password"),
            ssl=True
        )
    else:  # DEVELOPMENT/STAGING
        return EmailConfig(
            smtp_host=os.getenv("SMTP_HOST", "localhost"),
            smtp_port=int(os.getenv("SMTP_PORT", "1025")),
            username=os.getenv("SMTP_USER", "test@localhost"),
            password=os.getenv("SMTP_PASSWORD", "test_password"),
            ssl=False
        )


def create_logger() -> Logger:
    """Create logger based on environment"""
    env = get_environment()
    
    if env == Environment.PRODUCTION:
        return Logger("app", "INFO")
    elif env == Environment.STAGING:
        return Logger("app", "INFO")
    else:  # DEVELOPMENT
        return Logger("app", "DEBUG")


def create_database_service() -> DatabaseService:
    """Create database service with configuration"""
    config = Dependency.resolve(DatabaseConfig)
    return DatabaseService(config)


def create_cache_service() -> CacheService:
    """Create cache service with configuration"""
    config = Dependency.resolve(CacheConfig)
    return CacheService(config)


def create_email_service() -> EmailService:
    """Create email service with configuration"""
    config = Dependency.resolve(EmailConfig)
    return EmailService(config)


def create_application_service() -> ApplicationService:
    """Create application service with all dependencies"""
    db = Dependency.resolve(DatabaseService)
    cache = Dependency.resolve(CacheService)
    email = Dependency.resolve(EmailService)
    logger = Dependency.resolve(Logger)
    
    return ApplicationService(db, cache, email, logger)


# Setup Dependencies
def setup_dependencies():
    """Setup dependencies with configuration-based factories"""
    
    # Register configuration factories
    Dependency.register(DatabaseConfig, factory=create_database_config)
    Dependency.register(CacheConfig, factory=create_cache_config)
    Dependency.register(EmailConfig, factory=create_email_config)
    Dependency.register(Logger, factory=create_logger)
    
    # Register service factories
    Dependency.register(DatabaseService, factory=create_database_service)
    Dependency.register(CacheService, factory=create_cache_service)
    Dependency.register(EmailService, factory=create_email_service)
    Dependency.register(ApplicationService, factory=create_application_service)


# Main Application
async def main():
    """Main application demonstrating configuration-based factories"""
    print("🚀 Configuration Factory Example")
    
    # Show current environment
    env = get_environment()
    print(f"🌍 Environment: {env.value}")
    
    # Setup dependencies
    setup_dependencies()
    
    # Get application service
    app_service = Dependency.resolve(ApplicationService)
    
    # Process user registration
    await app_service.process_user_registration(
        name="Alice Johnson",
        email="alice@example.com"
    )
    
    print("🎉 Configuration factory example completed!")


if __name__ == "__main__":
    # Set environment for demonstration
    os.environ["APP_ENV"] = "development"
    asyncio.run(main())
