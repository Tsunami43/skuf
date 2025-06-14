# Skuf 
![Python](https://img.shields.io/badge/python-3.7%2B-blue?logo=python&logoColor=white)![Version](https://img.shields.io/badge/version-0.1.0-green)

Minimal Dependency Injection Container for Python

## 🚀 Features

- ✨ Lightweight and minimal
- ✅ Pythonic and explicit
- 🧱 Suitable for scripts, CLIs, and microservices

## 📦 Installation

```bash
pip install skuf
```

## 📝 Usage
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
