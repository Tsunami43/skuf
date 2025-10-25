"""
Web API Example - FastAPI with Dependency Injection
Demonstrates building a REST API with automatic dependency management.
"""
import asyncio
from typing import List, Optional
from dataclasses import dataclass
from fastapi import FastAPI, HTTPException, Depends
from skuf.dependency import Dependency


# Data Models
@dataclass
class User:
    id: int
    name: str
    email: str
    is_active: bool = True


@dataclass
class Product:
    id: int
    name: str
    price: float
    stock: int


# Services
class DatabaseService:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self._users = [
            User(1, "Alice Johnson", "alice@example.com"),
            User(2, "Bob Smith", "bob@example.com"),
        ]
        self._products = [
            Product(1, "Laptop", 999.99, 10),
            Product(2, "Mouse", 29.99, 50),
        ]
    
    def get_user(self, user_id: int) -> Optional[User]:
        return next((u for u in self._users if u.id == user_id), None)
    
    def get_all_users(self) -> List[User]:
        return self._users
    
    def create_user(self, name: str, email: str) -> User:
        user_id = len(self._users) + 1
        user = User(user_id, name, email)
        self._users.append(user)
        return user
    
    def get_product(self, product_id: int) -> Optional[Product]:
        return next((p for p in self._products if p.id == product_id), None)
    
    def get_all_products(self) -> List[Product]:
        return self._products


class CacheService:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self._cache = {}
    
    def get(self, key: str) -> Optional[str]:
        print(f"Cache GET {key} from {self.redis_url}")
        return self._cache.get(key)
    
    def set(self, key: str, value: str, ttl: int = 3600):
        print(f"Cache SET {key}={value} (TTL: {ttl}s)")
        self._cache[key] = value


class Logger:
    def __init__(self, name: str):
        self.name = name
    
    def info(self, message: str):
        print(f"[INFO] {self.name}: {message}")
    
    def error(self, message: str):
        print(f"[ERROR] {self.name}: {message}")


# Business Logic
class UserService:
    def __init__(self, db: DatabaseService, cache: CacheService, logger: Logger):
        self.db = db
        self.cache = cache
        self.logger = logger
    
    def get_user(self, user_id: int) -> Optional[User]:
        cache_key = f"user:{user_id}"
        cached = self.cache.get(cache_key)
        if cached:
            self.logger.info(f"User {user_id} found in cache")
            return User(1, cached, "cached@example.com")
        
        user = self.db.get_user(user_id)
        if user:
            self.cache.set(cache_key, user.name)
            self.logger.info(f"User {user_id} cached")
        
        return user
    
    def create_user(self, name: str, email: str) -> User:
        self.logger.info(f"Creating user: {name}")
        user = self.db.create_user(name, email)
        self.logger.info(f"User created with ID: {user.id}")
        return user


# Setup Dependencies
def setup_dependencies():
    Dependency.register(DatabaseService, instance=DatabaseService("postgresql://localhost/api"))
    Dependency.register(CacheService, instance=CacheService("redis://localhost:6379"))
    Dependency.register(Logger, instance=Logger("api"))


# FastAPI Dependencies
def get_user_service() -> UserService:
    @Dependency.inject
    def create_user_service(db: Dependency[DatabaseService], cache: Dependency[CacheService], 
                          logger: Dependency[Logger]):
        return UserService(db, cache, logger)
    
    return create_user_service()


# FastAPI App
app = FastAPI(title="User API", description="REST API with Dependency Injection")


@app.on_event("startup")
async def startup_event():
    setup_dependencies()
    print("🚀 Dependencies initialized!")


@app.get("/users", response_model=List[dict])
async def get_users(user_service: UserService = Depends(get_user_service)):
    """Get all users"""
    users = user_service.get_user(1)  # Example: get first user
    return [{"id": u.id, "name": u.name, "email": u.email} for u in [users] if u]


@app.get("/users/{user_id}", response_model=dict)
async def get_user(user_id: int, user_service: UserService = Depends(get_user_service)):
    """Get user by ID"""
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "name": user.name, "email": user.email}


@app.post("/users", response_model=dict)
async def create_user(name: str, email: str, user_service: UserService = Depends(get_user_service)):
    """Create new user"""
    user = user_service.create_user(name, email)
    return {"id": user.id, "name": user.name, "email": user.email}


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
