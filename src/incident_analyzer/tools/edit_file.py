from pathlib import Path
from pydantic import BaseModel, Field
from langchain_core.tools import tool
import difflib


class EditFileInput(BaseModel):
    file_path: str = Field(description="Path of the file to edit")
    old_code: str = Field(description="Exact existing code that should be replaced")
    new_code: str = Field(description="New corrected code")
    dry_run: bool = Field(
        default=True,
        description="If true, do not write to disk — only return a preview diff.",
    )


@tool
def edit_file(
    file_path: str, old_code: str, new_code: str, dry_run: bool = True
) -> str:
    """Propose or apply an edit to a file. Use dry_run=True first to preview a change
    before it is applied. The actual write to disk only happens when dry_run=False."""

    path = Path(file_path)

    if not path.exists():
        return f"File not found: {file_path}"

    content = path.read_text(encoding="utf-8")

    occurrences = content.count(old_code)

    if occurrences == 0:
        return "old_code not found in file — no match, nothing changed."

    if occurrences > 1:
        return (
            f"old_code matched {occurrences} times in the file. "
            f"Refusing to edit an ambiguous match — include more "
            f"surrounding context in old_code to make it unique."
        )

    updated_content = content.replace(old_code, new_code, 1)

    diff = "\n".join(
        difflib.unified_diff(
            content.splitlines(),
            updated_content.splitlines(),
            fromfile=file_path,
            tofile=file_path,
            lineterm="",
        )
    )

    if dry_run:
        return f"DRY RUN — no changes written.\n\nProposed diff:\n{diff}"

    path.write_text(updated_content, encoding="utf-8")
    return f"Successfully edited {file_path}\n\nApplied diff:\n{diff}"
