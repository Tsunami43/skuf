# Настройка после обновления Python

## Что нужно сделать после установки Python 3.8+

1. **Создать новое виртуальное окружение:**
```bash
# Удалить старое окружение
rm -rf venv

# Создать новое с Python 3.8+
python3.8 -m venv venv
# или
python3.9 -m venv venv
# или
python3.10 -m venv venv
# и т.д.
```

2. **Активировать окружение:**
```bash
source venv/bin/activate
```

3. **Установить зависимости:**
```bash
pip install --upgrade pip setuptools wheel build
pip install -r requirements-dev.txt
```

4. **Установить пакет в режиме разработки:**
```bash
pip install -e .
```

5. **Протестировать установку:**
```bash
python -c "from skuf import Dependency; print('✅ Skuf успешно импортирован!')"
```

6. **Запустить тесты:**
```bash
python -m pytest tests/ -v
```

7. **Запустить примеры:**
```bash
python examples/fastapi_style_uow.py
```

## Новые возможности API

После обновления вы сможете использовать новый упрощенный API:

```python
from skuf import Dependency

# Регистрация зависимостей
Dependency.register(MyService)
Dependency.register(MyUoW, context_manager=create_uow)

# Использование с автоматическим управлением контекстом
@Dependency.inject
def my_function(service: Dependency[MyService], uow: Dependency[MyUoW]):
    # Контекст автоматически управляется
    uow.add_operation("test")
    service.do_something()
```

## Публикация пакета

После настройки окружения:

```bash
# Сборка пакета
python -m build

# Публикация в PyPI (если нужно)
twine upload dist/*
```
