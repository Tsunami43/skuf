# Установка и настройка Skuf

## Требования

- Python 3.8 или выше
- pip (рекомендуется последняя версия)

## Установка в режиме разработки

1. Клонируйте репозиторий:
```bash
git clone https://github.com/Tsunami43/skuf.git
cd skuf
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
# или для Python 3.8+
python3.8 -m venv venv
python3.9 -m venv venv
# и т.д.
```

3. Активируйте виртуальное окружение:
```bash
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

4. Обновите pip и установите зависимости:
```bash
pip install --upgrade pip setuptools wheel build
```

5. Установите пакет в режиме разработки:
```bash
pip install -e .
```

## Сборка пакета

Для сборки пакета для публикации:

```bash
python -m build
```

Это создаст файлы в папке `dist/`:
- `skuf-0.2.1-py3-none-any.whl` (wheel)
- `skuf-0.2.1.tar.gz` (source distribution)

## Публикация в PyPI

1. Установите twine:
```bash
pip install twine
```

2. Загрузите пакет:
```bash
twine upload dist/*
```

## Тестирование

Запуск тестов:
```bash
python -m pytest tests/ -v
```

Запуск примеров:
```bash
python examples/fastapi_style_uow.py
python examples/async_generator_uow.py
python examples/uow_example.py
```

## Миграция с Poetry

Если вы ранее использовали Poetry:

1. Удалите `poetry.lock` (уже удален)
2. Используйте `pip install -e .` вместо `poetry install`
3. Используйте `python -m build` вместо `poetry build`
4. Используйте `twine upload` вместо `poetry publish`
