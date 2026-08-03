from .state import ErrorState


def build_extractor_prompt(state: ErrorState) -> str:
    return f"""
    The user pasted the following raw text containing an error, logs,
    and possibly a description and tech stack, all mixed together:

    {state['raw_text']}

    Extract the following from it:
    - error: the core error message
    - logs: relevant log lines
    - description: any explanation/context the user gave (empty string if none)
    - tech_stack: tech stack mentioned (empty string if not mentioned)
    """


def build_risk_prompt(state: ErrorState) -> str:
    return f"""
    Error: {state['error']}
    Logs: {state['logs']}
    Description: {state['description']}
    Tech Stack: {state['tech_stack']}

    Analyze the above and identify the risk level of this incident.
    """


def build_error_explanation_prompt(state: ErrorState) -> str:
    return f"""
     Error:{state['error']}
     Logs:{state['logs']}
     Description:{state['description']}
     Tech stack:{state['tech_stack']}
     
     Analyze the above error and explain clearly why it happened and why this risk level applies.
     """

def build_error_prevention_prompt(state: ErrorState) -> str:
    return f"""
        Error:{state['error']}
        Logs:{state['logs']}
        Description:{state['description']}
        Tech Stack:{state['tech_stack']}
        
        Analyze the above error and give proper steps to prevent it from happening again.
       """

