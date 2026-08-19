from pathlib import Path
from langchain_core.tools import tool

IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "myvenv",
    "node_modules",
    "__pycache__",
}

IGNORED_FILES = {
    ".env",
}


@tool
def search_files(
    query: str,
    directory: str = ".",
    max_results: int = 20,
) -> str:
    """
    Search source files in the workspace for a text, variable,
    function, class, or symbol.

    Returns matching file paths and line numbers.
    Does not return entire files.
    """

    if not query or not query.strip():
        return "Search query cannot be empty."

    root = Path(directory)

    if not root.exists():
        return f"Directory not found: {directory}"

    if not root.is_dir():
        return f"Not a directory: {directory}"

    query = query.strip()
    results = []

    allowed_extensions = {
        ".py",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".java",
        ".cpp",
        ".c",
        ".h",
        ".hpp",
        ".html",
        ".css",
        ".json",
        ".yaml",
        ".yml",
        ".md",
    }

    try:
        for path in root.rglob("*"):

            if any(part in IGNORED_DIRS for part in path.parts):
                continue

            if not path.is_file():
                continue

            if path.name in IGNORED_FILES:
                continue

            if path.suffix.lower() not in allowed_extensions:
                continue

            try:
                content = path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )
            except Exception:
                continue

            for line_number, line in enumerate(
                content.splitlines(),
                start=1,
            ):

                if query.lower() in line.lower():

                    results.append(f"{path} | line {line_number} | {line.strip()}")

                    if len(results) >= max_results:
                        break

            if len(results) >= max_results:
                break

    except Exception as error:
        return f"Search failed: {error}"

    if not results:
        return f"No matches found for: {query}"

    return f"Found {len(results)} match(es) for '{query}':\n" + "\n".join(results)
