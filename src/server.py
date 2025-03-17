import logging
import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from mcp import McpError
from mcp.types import ErrorData

from src.file_finder import find_files_by_path_fragment


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


mcp = FastMCP("file-finder-mcp", version="0.1.0")


@mcp.tool()
async def search_files(fragment: str, root_dir: str | None = None):
    """Обрабатывает запрос на поиск файлов."""
    try:
        if not fragment:
            raise McpError(ErrorData(
                code=400,
                message="Missing fragment"
            ))

        if not root_dir:
            root_dir = str(Path.home())

        results = find_files_by_path_fragment(root_dir, fragment)
        return {
            "content": [{
                "type": "text",
                "text": json.dumps(results, indent=4)
            }]
        }

    except Exception as e:
        logging.error(f"Ошибка при обработке запроса: {e}")
        raise McpError(ErrorData(
            code=500,
            message=f"Error searching files: {str(e)}"
        ))
