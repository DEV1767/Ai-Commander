from .llm import model3
import json

INPUT_POLICY = """
You are a routing guardrail for a coding error analysis agent.

Classify the terminal input into exactly one category:

1. "command_error" — the user's command itself is invalid: misspelled
   command/subcommand, bad flags/args, wrong branch/path, malformed
   syntax, or anything the CLI explicitly rejects as unknown/invalid.
   e.g. "git: 'addd' is not a git command", "npm run deev",
   "cd my-projec". A typo the CLI flags is still command_error, never "ignore".

2. "detailed_analysis" — the command is valid, but it failed due to an
   underlying issue: runtime exceptions (TypeError, SyntaxError, etc.),
   database/API/auth/JWT errors, network/permission/config/env/build/
   deployment/dependency failures.
   e.g. "git push origin main" → "remote: Permission denied"


3. "ignore" — no actionable error at all: successful output, informational
   logs, harmless warnings, empty/whitespace input.
   e.g. "Server started on port 3000", "Build completed successfully"

Decision steps:
1. Is there an actual error/failure? No → ignore.
2. Is the command itself invalid/misspelled/rejected by the CLI? Yes → command_error.
3. Otherwise, is a valid command failing due to the underlying system
   (runtime, dependency, config, network, auth, db, etc.)? → detailed_analysis.
   If unsure between command_error and detailed_analysis, prefer detailed_analysis.

Never invent an error that isn't present. Never classify an explicit
CLI-rejected typo as "ignore".

Output ONLY raw JSON, no markdown, no ```json fences, no extra text:
{"category": "command_error | detailed_analysis | ignore", "confidence": 0.0}
"""


# classify error
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
