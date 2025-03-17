# File Finder MCP Server

MCP сервер для поиска файлов по фрагменту пути.

## Установка

1. Установите Poetry (если еще не установлен):

```bash
pip install poetry
```

2. Убедитесь, что установлен Python 3.10+
3. Клонируйте проект
```bash
git clone https://github.com/LorinLex/test-opora-standart/ && cd test-opora-standart
```
5. Установите зависимости:

```bash
poetry install
```

## Запуск

```bash
poetry run python -m src.server
```

## Использование

Сервер предоставляет один инструмент:

### `search_files`

Поиск файлов по фрагменту пути.

**Параметры:**
- `fragment` (обязательный) - фрагмент пути для поиска
- `root_dir` (опциональный) - корневая директория для поиска (по умолчанию - домашняя директория)

**Пример использования:**

```json
{
  "name": "search_files",
  "arguments": {
    "fragment": "test",
    "root_dir": "/path/to/search"
  }
}
```

## Интеграция с CLine

Для добавления сервера в CLine выполните:

1. Убедитесь, что сервер запущен
2. Добавьте конфигурацию в settings.json CLine:

```json
{
  "mcpServers": {
    "file-finder": {
      "command": "poetry",
      "args": ["run", "python", "-m", "src.server"],
      "env": {
        "PYTHONPATH": "."
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## Пример промпта

Пример запроса для поиска файлов:

```
Найди все файлы, содержащие "test" в пути, начиная с директории /home/user/projects
```

Пример ответа:

```
Найдены следующие файлы:
- /home/user/projects/test_project/README.md
- /home/user/projects/old_tests/test.py
```

## Лицензия

MIT
