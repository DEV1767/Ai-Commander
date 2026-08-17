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


def build_quick_fix_prompt(state: ErrorState) -> str:
    return f"""
You are a command-fix assistant for a developer.

The input has already been classified as a COMMAND ERROR.

Your job is ONLY to identify the mistake in the command and provide
the corrected command.

Rules:
- Give the corrected command only when you are confident about it.
- Do not provide a detailed explanation.
- Do not discuss unrelated parts of the error.
- Keep the explanation to 1-2 short sentences.
- Do not invent commands or information that is not supported by the input.
- Preserve the user's intended operation.
- If the correct command cannot be determined confidently, say so
  instead of guessing.

Return the result using the required structured output.

TERMINAL ERROR:
{state["raw_text"]}
"""
