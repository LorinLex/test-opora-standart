import subprocess
import platform
import logging
from pathlib import Path
import json
from datetime import datetime
from time import time


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def escape_special_chars(path):
    """
    Экранирует специальные символы в пути для безопасного использования
    в командах.
    """
    return str(path).replace('"', '\\"').replace("'", "\\'")


def get_file_metadata(file_path):
    """Возвращает метаданные файла: имя, путь, размер и дату создания."""
    file_stat = file_path.stat()
    return {
        "name": file_path.name,
        "path": str(file_path),
        "size": file_stat.st_size,
        "created_at": datetime.fromtimestamp(file_stat.st_ctime).isoformat()
    }


def find_files_by_path_fragment(root_dir, path_fragment):
    """
    Ищет файлы по фрагменту пути в указанной директории и возвращает JSON
    с метаданными.
    """
    try:
        root_dir = Path(root_dir).absolute()
        path_fragment = escape_special_chars(path_fragment)
        logging.info(f"Поиск файлов в директории: {root_dir}")

        os_type = platform.system().lower()

        if os_type == 'windows':
            try:
                subprocess.run(
                    ['powershell', '-Command', 'echo test'],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            except (subprocess.CalledProcessError, FileNotFoundError):
                logging.error(
                    "PowerShell не доступен. Убедитесь, что он установлен."
                )
                return json.dumps([])

            command = [
                'powershell',
                '-Command',
                f'Get-ChildItem -Path "{root_dir}" -Recurse -File | '
                f'Where-Object {{ $_.Name -like "*{path_fragment}*" }} | '
                f'Select-Object -ExpandProperty FullName'
            ]
        else:
            try:
                subprocess.run(
                    ['find', '--version'],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            except (subprocess.CalledProcessError, FileNotFoundError):
                logging.error(
                    "Команда 'find' не доступна."
                    "Убедитесь, что она установлена."
                )
                return json.dumps([])

            command = [
                'bash', '-c',
                f'find "{root_dir}" -type f -wholename "*{path_fragment}*" 2>/dev/null'
            ]

        logging.info(f"Выполнение команды: {' '.join(command)}")
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )

        if result.returncode != 0:
            logging.warning(f"Ошибка при выполнении команды: {result.stderr}")

        files_metadata = []
        for line in result.stdout.splitlines():
            if line.strip():
                file_path = Path(line.strip())
                if file_path.exists() and file_path.is_file():
                    files_metadata.append(get_file_metadata(file_path))

        logging.info(f"Найдено файлов: {len(files_metadata)}")
        return json.dumps(files_metadata, indent=4, ensure_ascii=False)

    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        return json.dumps([])
