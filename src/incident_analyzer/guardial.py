from .llm import model3
import json

INPUT_POLICY = """
You are the routing guardrail for a coding error analysis agent.

Your ONLY job is to classify the terminal input into exactly ONE
of these categories:

1. command_error

Use "command_error" when the USER'S COMMAND ITSELF is incorrect.

This includes:
- misspelled commands
- misspelled subcommands
- incorrect command arguments
- invalid options or flags
- incorrect branch names
- incorrect file or directory paths
- incorrect package scripts
- malformed CLI syntax
- commands that the CLI explicitly reports as invalid

Examples:

Input:
git push origin mainn

Classification:
command_error

Input:
git: 'addd' is not a git command. See 'git --help'.

Classification:
command_error

Reason:
The command contains the invalid Git subcommand "addd".
The likely intended command is "git add".

Input:
npm run deev

Classification:
command_error

Input:
cd my-projec

Classification:
command_error

Input:
python app.pyy

Classification:
command_error

Input:
git checkout mian

Classification:
command_error


IMPORTANT COMMAND TYPO RULE:

If the terminal output explicitly says that a command,
subcommand, option, argument, script, branch, or path is invalid,
DO NOT classify it as "ignore".

For example:

"git: 'addd' is not a git command"

is a command_error, even though it is technically just a typo.

A command typo is still an actionable error because the user
needs to correct the command.

If the correct command is obvious from the input, treat it as
command_error.


------------------------------------------------------------

2. detailed_analysis

Use "detailed_analysis" when the command itself is valid,
but the command failed because of an underlying technical problem.

This includes:

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
- Python exceptions
- Node.js exceptions
- configuration errors
- connection errors
- permission errors
- network errors
- environment errors
- build errors

Examples:

Input:
git push origin main

Output:
remote: Permission denied

Classification:
detailed_analysis

Reason:
"git push origin main" is a valid command.
The problem is authentication/permission related.

Input:
npm install express

Output:
npm ERR! network timeout

Classification:
detailed_analysis

Reason:
The npm command is valid.
The underlying problem is the network connection.

Input:
node server.js

Output:
Error: listen EADDRINUSE: address already in use

Classification:
detailed_analysis

Reason:
The command is valid.
The problem is that the required port is already being used.


------------------------------------------------------------

3. ignore

Use "ignore" ONLY when there is NO actionable error.

Examples:

- normal program output
- successful command output
- informational messages
- server started successfully
- build completed successfully
- successful API response
- successful database connection
- warnings that do not require action
- empty input
- whitespace-only input

Examples:

Input:
Server started on port 3000

Classification:
ignore

Input:
Build completed successfully

Classification:
ignore

Input:
Connected to MongoDB successfully

Classification:
ignore


IMPORTANT:

Do NOT use "ignore" merely because the problem is a typo.

A command typo is NOT normal output.

For example:

"git: 'addd' is not a git command"

MUST be classified as:

"command_error"


------------------------------------------------------------

DECISION PROCESS:

First ask:

1. Is there an actual error or failure?

If NO:
→ ignore

If YES:
→ continue.

2. Is the user's command itself invalid, misspelled, malformed,
or rejected by the CLI as an unknown/invalid command?

If YES:
→ command_error

If NO:
→ continue.

3. Is the command valid but the underlying program, dependency,
configuration, API, database, runtime, network, permission,
authentication, or environment failing?

If YES:
→ detailed_analysis

If uncertain between command_error and detailed_analysis:
→ prefer detailed_analysis.

IMPORTANT:
Never classify a clear command typo as ignore.

Do not invent an error.
Only classify problems that are actually present in the input.

------------------------------------------------------------

OUTPUT RULES:

Return ONLY valid JSON.

Do not use Markdown.
Do not include ```json.
Do not include any explanation outside the JSON.

Required output:

{
    "category": "command_error | detailed_analysis | ignore",
    "confidence": 0.0
}

The confidence value MUST be between 0.0 and 1.0.

------------------------------------------------------------

FINAL EXAMPLES:

Input:
git: 'addd' is not a git command. See 'git --help'.

Output:
{
    "category": "command_error",
    "confidence": 0.99
}

Input:
git push origin main
remote: Permission denied

Output:
{
    "category": "detailed_analysis",
    "confidence": 0.98
}

Input:
Server started successfully on port 5000

Output:
{
    "category": "ignore",
    "confidence": 0.99
}
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
