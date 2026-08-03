from .llm import model, model2
from .prompts import (
    build_error_explanation_prompt,
    build_error_prevention_prompt,
    build_extractor_prompt,
    build_risk_prompt,
)
from .state import ErrorExtractor, ErrorState, Risk, Suggestion


def extractor_node(state: ErrorState) -> dict:
    """
     Extract the logs,error,description  from the raw_text.
    """
    
    structured_llm = model.with_structured_output(ErrorExtractor)
    response = structured_llm.invoke(build_extractor_prompt(state))

    return {
        "error": response.error,
        "logs": response.logs,
        "description": response.description,
        "tech_stack": response.tech_stack,
    }


def risk_analysis_node(state: ErrorState) -> dict:
    """
     Analyze the log,errors and on that basis return the risk of error in the term of high ,low and medium .
    """
    
    structured_llm = model.with_structured_output(Risk)
    response = structured_llm.invoke(build_risk_prompt(state))

    return {"risk": response.risk}


def error_explanation_node(state: ErrorState) -> dict:
    """
    Explain the error on the basis of logs,error and risk level. 
    """
    
    structured_llm = model2.with_structured_output(Suggestion)
    response = structured_llm.invoke(build_error_explanation_prompt(state))

    return {"explanation": response.explanation}


def error_prevention_node(state: ErrorState) -> dict:
    """
    Suggest the user how to prevent the error in future .
    """
    structured_llm = model2.with_structured_output(Suggestion)
    response = structured_llm.invoke(build_error_prevention_prompt(state))

    return {"prevention": response.prevention}

def route_by_risk(state:ErrorState)->str:
    """
    Check the risk of error and then help to explain the error.
    """
    
    if state['risk']=="Low":
       return "skip"
     
    return "analyze"