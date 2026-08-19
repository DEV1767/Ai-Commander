import subprocess
from pathlib import Path


def is_git_clean(project_root: Path) -> tuple[bool, str]:
    """
    Return (is_clean,message).
    is_clean is True only if there is a git repo AND there are no uncommitted changes.
    """
    try:
        result = subprocess.run(
            ["git", "status", "--procelain"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except FileNotFoundError:
        return False, "git is not installed or not available on PATH."
    except subprocess.TimeoutExpired:
        return False, "git status time .out"

    if result.returncode != 0:
        return False, f"Not a git repository or git error:{result.stderr.strip()}"

    if result.stdout.strip():
        return (
            False,
            "Uncommited changes detected. Commit or stash your chanegs before requesting an auto-fix.",
        )

    return True, "Clean."
