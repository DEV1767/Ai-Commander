from .llm import model3
import json

INPUT_POLICY = """
You are the routing guardrail for a coding error analysis agent.

Your ONLY job is to classify the terminal input into exactly ONE
of these categories:

1. command_error

The user entered an incorrect CLI command, argument, option,
branch name, file path, package script, or similar command input.

Examples:

- git push origin mainn
- npm run deev
- cd my-projec
- python app.pyy
- git checkout mian

Important:
Only classify something as command_error when the problem is
actually related to the command entered by the user.

------------------------------------------------------------

2. detailed_analysis

The input contains a genuine technical problem that requires
understanding the underlying cause.

Examples:

- TypeError
- ReferenceError
- SyntaxError
- database errors
- MongoDB errors
- Redis errors
- API errors
- authentication errors
- JWT errors
- deployment errors
- Vercel errors
- dependency errors
- package installation errors
- runtime errors
- configuration errors
- connection errors
- Python exceptions
- Node.js exceptions

------------------------------------------------------------

3. ignore

The input is NOT a meaningful error.

Examples:

- normal program output
- successful command output
- informational messages
- server started successfully
- build completed successfully
- warnings that do not require action
- empty input
- whitespace-only input

------------------------------------------------------------

IMPORTANT RULES:

- Do not invent an error.
- Do not classify normal output as an error.
- If the input clearly shows a command typo or incorrect command,
  classify it as command_error.
- If the command itself is correct but the underlying program,
  dependency, configuration, API, database, runtime, or environment
  has a problem, classify it as detailed_analysis.
- When uncertain between command_error and detailed_analysis,
  prefer detailed_analysis.
- confidence must be between 0.0 and 1.0.
- Return ONLY valid JSON.
- Do not use Markdown.
- Do not include ```json.
- Do not include any explanation outside the JSON.

Required output:

{
    "category": "command_error | detailed_analysis | ignore",
    "confidence": 0.0
}
"""


def classify_error(log: str) -> dict:
    """
    Classify terminal input before sending it to the
    detailed error-analysis pipeline.
    """

    if not log or not log.strip():
        return {"category": "ignore", "confidence": 1.0}

    prompt = f"""
{INPUT_POLICY}

TERMINAL INPUT:

{log}
"""
    try:

        response = model3.invoke(prompt)

        content = response.content

        if not isinstance(content, str):
            content = str(content)

        content = content.strip()

        result = json.loads(content)

        category = result.get("category")
        confidence = result.get("confidence", 0.0)

        valid_categories = {"command_error", "detailed_analysis", "ignore"}

        if category not in valid_categories:

            return {"category": "detailed_analysis", "confidence": 0.0}

        try:
            confidence = float(confidence)
        except (TypeError, ValueError):

            confidence = 0.0

        confidence = max(0.0, min(1.0, confidence))
        return {"category": category, "confidence": confidence}

    except json.JSONDecodeError as error:

        print("Guardrail JSON error:", error)

        return {"category": "detailed_analysis", "confidence": 0.0}

    except Exception as error:

        print("Guardrail classification error:", error)

        return {"category": "detailed_analysis", "confidence": 0.0}
