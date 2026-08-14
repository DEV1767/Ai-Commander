from fastapi import FastAPI
from pydantic import BaseModel

from src.incident_analyzer.graph import build_graph

app = FastAPI()

graph = build_graph()


class analyzeRequest(BaseModel):
    log: str


@app.post("/analyze")
def analyze(request: analyzeRequest):
    initial_state = {
        "raw_text": request.log,
    }
    result=graph.invoke(initial_state)
    
    return result