import subprocess
import platform
import logging
from pathlib import Path
from datetime import datetime
from time import time


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def escape_special_chars(path: str | Path):
    """
    Экранирует специальные символы в пути для безопасного использования
    в командах.
    """
    return str(path).replace('"', '\\"').replace("'", "\\'")


def get_file_metadata(file_path: Path):
    """Возвращает метаданные файла: имя, путь, размер и дату создания."""
    file_stat = file_path.stat()
    return {
        "name": file_path.name,
        "path": str(file_path),
        "size": file_stat.st_size,
        "created_at": datetime.fromtimestamp(file_stat.st_ctime).isoformat()
    }


def find_files_by_path_fragment(
    root_dir_raw: str,
    path_fragment: str
) -> list[dict[str, str]]:
    """
    Ищет файлы по фрагменту пути в указанной директории и возвращает список
    метаданных.
    """
    root_dir = Path(root_dir_raw).absolute()
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
            error_msg = "PowerShell не доступен. Убедитесь, что он установлен."
            logging.error(error_msg)
            raise RuntimeError(error_msg)

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
            error_msg = "Команда 'find' не доступна." \
                        "Убедитесь, что она установлена."
            logging.error(error_msg)
            raise RuntimeError(error_msg)

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
    return files_metadata


# Пример использования:
if __name__ == "__main__":
    root_directory = str(Path.home())  # Для Linux/macOS
    # root_directory = 'C:\\path\\to\\search'  # Для Windows
    fragment = 'src/server.py'
    start = time()
    result_json = find_files_by_path_fragment(root_directory, fragment)
    print(result_json)
    print(f"Exec time: {time() - start}")
