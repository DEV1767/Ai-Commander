import subprocess
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.incident_analyzer.git_utils import is_git_clean
from src.incident_analyzer.graph import build_graph, build_correction_graph
from src.incident_analyzer.tools.edit_file import edit_file

app = FastAPI()

graph = build_graph()
correction_graph = build_correction_graph()

PROJECT_ROOT = Path(__file__).resolve().parent


class analyzeRequest(BaseModel):
    log: str


class CorrectRequest(BaseModel):
    error: str
    logs: str = ""
    description: str = ""
    tech_stack: str = ""
    can_fix: bool = False


class ConfirmRequest(BaseModel):
    file_path: str
    old_code: str
    new_code: str


@app.get("/")
def root():
    return {"message": "Agent server is running"}


@app.post("/analyze")
def analyze(request: analyzeRequest):
    initial_state = {
        "raw_text": request.log,
    }
    result = graph.invoke(initial_state)

    return result


@app.post("/correct")
def correct(request: CorrectRequest):

    if not request.can_fix:
        raise HTTPException(
            status_code=400,
            detail="This issue was not marked as auto-fixable by /analyze.",
        )

    action_state = {
        "error": request.error,
        "logs": request.logs,
        "description": request.description,
        "tech_stack": request.tech_stack,
    }

    result = correction_graph.invoke(action_state)

    return {
        "action_response": result.get("action_response", ""),
        "tool_used": result.get("tool_used", []),
        "proposed_edit": result.get("proposed_edit"),
    }


@app.post("/correct/confirm")
def correct_confirm(request: ConfirmRequest):

    clean, message = is_git_clean(PROJECT_ROOT)
    if not clean:
        raise HTTPException(status_code=409, detail=message)

    edit_result = edit_file.invoke(
        {
            "file_path": request.file_path,
            "old_code": request.old_code,
            "new_code": request.new_code,
            "dry_run": False,
        }
    )

    if "Successfully edited" not in str(edit_result):
        raise HTTPException(
            status_code=400,
            detail=f"Edit could not be applied: {edit_result}",
        )

    commit = subprocess.run(
        ["git", "commit", "-am", f"Auto-fix: {request.file_path}"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    return {
        "edit_result": edit_result,
        "commit_output": commit.stdout.strip() or commit.stderr.strip(),
    }


@app.post("/undo-last-fix")
def undo_last_fix():

    log = subprocess.run(
        ["git", "log", "-1", "--pretty=%s"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    if not log.stdout.strip().startswith("Auto-fix:"):
        raise HTTPException(
            status_code=400,
            detail="Last commit was not an auto-fix; refusing to revert.",
        )

    result = subprocess.run(
        ["git", "revert", "--no-edit", "HEAD"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail=f"Revert failed: {result.stderr.strip()}",
        )

    return {"message": "Last auto-fix reverted.", "output": result.stdout.strip()}
