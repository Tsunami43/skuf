# Factory Pattern Examples

This directory contains examples demonstrating different factory patterns with Skuf dependency injection.

## 📁 Factory Examples Overview

### 1. `factory_pattern_example.py` - Basic Factory Pattern
**Lines: ~100** | **Use Case: Service Creation**

Demonstrates basic factory pattern for creating services:

- **Factory Functions** - Creating services with dependencies
- **Service Injection** - Automatic dependency resolution
- **Resource Management** - Database and cache connections
- **Business Logic** - User service with notifications

**Key Features:**
- Factory functions for service creation
- Dependency injection in factories
- Service composition
- Resource lifecycle management

```bash
# Run the example
python examples/factory_pattern_example.py
```

### 2. `context_manager_factory_example.py` - Context Manager Factories
**Lines: ~100** | **Use Case: Resource Management**

Shows how to use factories to create context managers:

- **Sync Context Managers** - Database transactions
- **Async Context Managers** - Cache sessions
- **Async Generator Factories** - Complex resource management
- **Resource Lifecycle** - Automatic cleanup

**Key Features:**
- Context manager factories
- Resource lifecycle management
- Transaction handling
- Error handling and cleanup

```bash
# Run the example
python examples/context_manager_factory_example.py
```

### 3. `configuration_factory_example.py` - Configuration-based Factories
**Lines: ~100** | **Use Case: Environment Configuration**

Demonstrates environment-based service creation:

- **Environment Detection** - Development/Staging/Production
- **Configuration Objects** - Type-safe configuration
- **Service Factories** - Environment-specific services
- **Dependency Injection** - Configuration-based wiring

**Key Features:**
- Environment-based configuration
- Type-safe configuration objects
- Service factory composition
- Configuration injection

```bash
# Run the example
python examples/configuration_factory_example.py
```

## 🏭 Factory Patterns Demonstrated

### 1. **Basic Factory Pattern**
```python
def create_user_service() -> UserService:
    # Get dependencies
    db = Dependency.resolve(DatabaseService)
    cache = Dependency.resolve(CacheService)
    logger = Dependency.resolve(Logger)
    
    return UserService(db, cache, logger)

# Register factory
Dependency.register(UserService, factory=create_user_service)
```

### 2. **Context Manager Factory**
```python
def create_database_context_manager():
    return DatabaseContextManager(
        host="localhost",
        port=5432,
        database="myapp"
    )

# Register context manager factory
Dependency.register(DatabaseContextManager, factory=create_database_context_manager)
```

### 3. **Configuration Factory**
```python
def create_database_service() -> DatabaseService:
    config = Dependency.resolve(DatabaseConfig)
    return DatabaseService(config)

# Register configuration and service factories
Dependency.register(DatabaseConfig, factory=create_database_config)
Dependency.register(DatabaseService, factory=create_database_service)
```

### 4. **Async Generator Factory**
```python
@asynccontextmanager
async def get_database_session():
    session = DatabaseSession(session_id=f"async-db-{datetime.now().timestamp()}")
    try:
        yield session
        print("✅ Transaction committed")
    except Exception as e:
        print(f"❌ Transaction rolled back: {e}")
    finally:
        session.connected = False

# Register async generator factory
Dependency.register('DatabaseSession', factory=get_database_session)
```

## 🔧 Factory Pattern Benefits

### **1. Lazy Initialization**
- Services are created only when needed
- Reduces startup time
- Memory efficient

### **2. Configuration Management**
- Environment-specific configurations
- Type-safe configuration objects
- Easy testing with different configs

### **3. Resource Management**
- Automatic resource cleanup
- Context manager support
- Transaction handling

### **4. Dependency Composition**
- Complex service creation
- Dependency injection in factories
- Service composition

## 📚 Use Cases Covered

- **Service Creation** - Basic factory pattern
- **Resource Management** - Context managers
- **Configuration** - Environment-based setup
- **Database Connections** - Connection management
- **Cache Services** - Cache connection handling
- **Email Services** - SMTP configuration
- **Logging** - Environment-specific logging
- **Transactions** - Database transaction management

## 🎯 When to Use Factories

### **Use Factories When:**
- Services need complex initialization
- Configuration varies by environment
- Resources need lifecycle management
- Services have many dependencies
- You need lazy initialization

### **Use Instance When:**
- Simple services with no dependencies
- Singleton services
- Stateless services
- Services with default configuration

## 🔍 Code Quality Features

- **Type Hints** - Full type annotation
- **Error Handling** - Comprehensive error management
- **Resource Cleanup** - Automatic resource management
- **Configuration** - Environment-based setup
- **Testing** - Easy to mock and test
- **Documentation** - Clear factory documentation

## 📖 Learning Path

1. **Start with `factory_pattern_example.py`** - Basic factory pattern
2. **Move to `context_manager_factory_example.py`** - Resource management
3. **Explore `configuration_factory_example.py`** - Environment configuration

Each example builds upon the previous concepts while introducing new patterns.

## 🚀 Quick Start

```bash
# Install dependencies
pip install skuf

# Run examples
python examples/factory_pattern_example.py
python examples/context_manager_factory_example.py
python examples/configuration_factory_example.py
```

## 📝 Notes

- All examples are production-ready patterns
- Factories provide better control over service creation
- Context managers ensure proper resource cleanup
- Configuration factories enable environment-specific setups
- Easy to extend and modify for your use case
