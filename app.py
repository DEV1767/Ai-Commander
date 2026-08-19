from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.incident_analyzer.graph import build_graph, build_correction_graph

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