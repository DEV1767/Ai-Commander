from pathlib import Path
from pydantic import BaseModel, Field
from langchain_core.tools import tool

class EditFileInput(BaseModel):
    file_path: str = Field(description="Path of the file to edit")
    old_code: str = Field(description="Exact exixting code that should be replaced")
    new_code: str = Field(description="New corrected code")

@tool
def edit_file(file_path: str, old_code: str, new_code: str) -> str:
        
    """Edit files and folders available in a workspace directory."""

    path = Path(file_path)

    if not path.exists():
        return f"File not found:{file_path}"

    content = path.read_text(encoding="utf-8")

    if old_code not in content:
        return "The old file was not changed."
    updated_content = content.replace(old_code, new_code, 1)

    path.write_text(updated_content, encoding="utf-8")

    return f"Successfully edited {file_path}"
