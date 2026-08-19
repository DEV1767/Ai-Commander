from pathlib import Path
from langchain_core.tools import tool


@tool
def read_file(file_path: str, start_line: int = 1, end_line: int = 50) -> str:
    """
    Read a portion of a file.
    """

    path = Path(file_path)

    if not path.exists():
        return f"File not found: {file_path}"

    try:
        lines = path.read_text(encoding="utf-8").splitlines()

        selected_lines = lines[start_line - 1 : end_line]

        return "\n".join(
            f"{i + start_line} | {line}" for i, line in enumerate(selected_lines)
        )

    except Exception as e:
        return f"Error reading file: {str(e)}"
