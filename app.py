from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.incident_analyzer.graph import build_graph, build_correction_graph
from src.incident_analyzer.prompts import build_suggest_fix_prompt
from src.incident_analyzer.state import SuggestedFix
from src.incident_analyzer.llm import structured_call

app = FastAPI()

graph = build_graph()
correction_graph = build_correction_graph()


class analyzeRequest(BaseModel):
    log: str


class CorrectRequest(BaseModel):
    error: str
    logs: str = ""
    description: str = ""
    tech_stack: str = ""
    can_fix: bool = False


class SuggestFixRequest(BaseModel):
    error: str
    logs: str = ""
    description: str = ""
    tech_stack: str = ""
    file_path: str
    file_content: str


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
    }


@app.post("/suggest-fix")
def suggest_fix(request: SuggestFixRequest):
    """
    No filesystem access, no tools — the caller sends local file content
    directly. Returns old_code/new_code for the caller to apply itself.
    Called only from the Node backend (server-to-server), never directly
    from the extension or webview.
    """

    prompt = build_suggest_fix_prompt(
        error=request.error,
        logs=request.logs,
        description=request.description,
        tech_stack=request.tech_stack,
        file_path=request.file_path,
        file_content=request.file_content,
    )

    result = structured_call(
        model_name="openai/gpt-oss-120b",
        prompt=prompt,
        schema=SuggestedFix.model_json_schema(),
        schema_name="suggested_fix",
    )

    if not result.get("can_fix"):
        raise HTTPException(
            status_code=400,
            detail=result.get("explanation", "Could not determine a confident fix."),
        )

    if result.get("old_code", "") not in request.file_content:
        raise HTTPException(
            status_code=422,
            detail="The suggested old_code does not exactly match the provided file content.",
        )

    return {
        "file_path": request.file_path,
        "old_code": result["old_code"],
        "new_code": result["new_code"],
        "explanation": result.get("explanation", ""),
    }
