from pathlib import Path
from langchain_core.tools import tool


IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "myvenv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    "dist",
    "build",
}

@tool
def list_files(
    directory: str = ".",
    max_files: int =30,
) -> str:
    """
    List useful project files while ignoring
    virtual environments, dependencies and build files.
    """

    root = Path(directory).resolve()

    if not root.exists():
        return f"Directory not found: {directory}"

    if not root.is_dir():
        return f"Not a directory: {directory}"

    files = []

    try:

        for path in root.rglob("*"):

         
            if any(part in IGNORED_DIRS for part in path.parts):
                continue

            if path.is_file():

                relative_path = path.relative_to(root)

                files.append(str(relative_path))


                if len(files) >= max_files:
                    break

    except Exception as error:
        return f"Error while listing files: {error}"

    if not files:
        return "No project files found."

    result = "\n".join(files)

    if len(files) >= max_files:
        result += f"\n\nShowing first {max_files} files only."

    return result
