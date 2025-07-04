# Skuf 
![Python](https://img.shields.io/badge/python-3.7%2B-blue?logo=python&logoColor=white)![Version](https://img.shields.io/badge/version-0.2.0-green)

Minimal Dependency Injection & Configuration Framework for Python

## 🚀 Features

- ⚡️ Lightweight and zero-dependency
- 🧩 Simple Dependency Injection container
- 🔐 Type-safe `.env`-based configuration loader (like `pydantic.BaseSettings`)
- 🧱 Suitable for scripts, CLI tools, microservices

## 📦 Installation

```bash
pip install skuf
```

## 🧰 Dependency Injection
```python
from skuf import DIContainer, Dependency

# Define a Logger
class Logger:
    def log(self, msg: str):
        print(msg)


DIContainer.register(Logger) # Register the class

logger = DIContainer.resolve(Logger)

def test_func(logger = Dependency(Logger)):
    logger.log("Hello, World! From a function!")

logger.log("Hello, World!")
test_func()

# Output:
# Hello, World!
# Hello, World! From a function!
```


## ⚙️ Environment Settings
```python
# .env
API_KEY=supersecret
TIMEOUT=5
DEBUG=true
RETRIES=3
ADMINS=123|456

# settings.py
from skuf import BaseSettings
from typing import List

class Settings(BaseSettings):
    api_key: str
    timeout: int
    debug: bool
    retries: int
    admins: List[int]

settings = Settings()

print(settings.api_key)   # supersecret
print(settings.timeout)   # 5
print(settings.debug)     # True
print(settings.admins)    # [123, 456]
```

✅ Supports types:
* str, int, float, bool
* List[str], List[int], List[float] (via pipe-separated values like A|B|C)
