from .state import ErrorState

# v2 Prompts


def build_extractor_prompt(state: ErrorState) -> str:
    return f"""
The user pasted the following raw text containing an error, logs,
and possibly a description and tech stack, all mixed together:

{state['raw_text']}

Extract the following:

- error: the core error message
- logs: relevant log lines
- description: any explanation/context the user gave (empty string if none)
- tech_stack: tech stack mentioned (empty string if not mentioned)
"""


def build_risk_prompt(state: ErrorState) -> str:
    return f"""
Error:
{state['error']}

Logs:
{state['logs']}

Description:
{state['description']}

Tech Stack:
{state['tech_stack']}

Analyze the above and identify the risk level of this incident.
"""


def build_error_explanation_prompt(state: ErrorState) -> str:
    return f"""
Error:
{state['error']}

Logs:
{state['logs']}

Description:
{state['description']}

Tech Stack:
{state['tech_stack']}

Analyze the above error and explain clearly:

1. Why the error happened.
2. What is causing the error.
3. Why this risk level applies.
"""


def build_error_prevention_prompt(state: ErrorState) -> str:
    return f"""
Error:
{state['error']}

Logs:
{state['logs']}

Description:
{state['description']}

Tech Stack:
{state['tech_stack']}

Analyze the above error and give practical steps
to prevent it from happening again.
"""


def build_quick_fix_prompt(state: ErrorState) -> str:
    return f"""
You are a command-fix assistant for a developer.

The input has already been classified as a COMMAND ERROR.

Your job is to:

1. Give a short, specific title for the error.
   Examples:
   - "Git subcommand not recognized"
   - "PowerShell command not found"
   - "Invalid npm script"

   Never output "Unknown error" or any vague/generic placeholder.

2. Determine whether a corrected command can be confidently identified.

   Set has_fix to true only if you are confident.

3. If has_fix is true, provide the corrected command in quick_fix.

4. If has_fix is false, set quick_fix to an empty string.

Rules:

- Give the corrected command only when you are confident.
- Do not provide a detailed explanation.
- Do not discuss unrelated parts of the error.
- Keep the explanation to 1-2 short sentences.
- Do not invent commands or information.
- Preserve the user's intended operation.
- If the correct command cannot be determined confidently,
  set has_fix to false and explain briefly why.

TERMINAL ERROR:

{state["raw_text"]}
"""


# V3 - DECIDE WHETHER ERROR
# CAN BE FIXED


def build_action_decision_prompt(state: ErrorState) -> str:
    return f"""
You are deciding whether a coding error can be automatically
corrected by modifying source code.

Error:
{state.get("error", "")}

Description:
{state.get("description", "")}

Logs:
{state.get("logs", "")}

Tech Stack:
{state.get("tech_stack", "")}

Your task is ONLY to decide whether this error is reasonably
fixable by changing source code.

Set can_fix=true when:

- The error is caused by incorrect source code.
- The required correction can reasonably be determined.
- The correction can potentially be made using an edit to the code.

Examples:

- Undefined variable
- Incorrect function usage
- Missing import
- Syntax error
- Wrong variable name
- Incorrect API usage visible from the code
- Incorrect condition or logic that can be determined from the code

Set can_fix=false when the problem primarily requires:

- API keys
- Credentials
- Permissions
- External services
- Infrastructure changes
- Database availability
- Network availability
- Environment configuration that cannot be determined
- User decisions
- Missing external resources
- Information that cannot be determined safely

IMPORTANT:

Do NOT inspect files.
Do NOT call tools.
Do NOT modify files.

You are only deciding whether a code correction is potentially possible.

Return the structured result.
"""


# V3 - ACTION AGENT

def build_action_node_prompt(state: ErrorState) -> str:
    return f"""
You are an AI coding debugging agent.

Your job is to investigate and fix the coding error by inspecting the
minimum amount of source code necessary.

ERROR:
{state.get("error", "")}

LOGS:
{state.get("logs", "")}

DESCRIPTION:
{state.get("description", "")}

TECH STACK:
{state.get("tech_stack", "")}


IMPORTANT RETRIEVAL RULES:

1. DO NOT inspect the entire repository.

2. If the error already contains a file path:
   - Do NOT call list_files.
   - Directly use read_file on that file.

3. If the error contains a line number:
   - Read only a small range around that line.
   - Start with approximately 20 lines before and 20 lines after it.

4. If the file path is unknown:
   - Use list_files to locate the relevant file.
   - Do not read every file.

5. After reading a file, decide whether you have enough information.

6. Only read another file if the first file references code that is
   necessary to understand the error.

7. Follow dependencies progressively:

   error
      ↓
   relevant file
      ↓
   relevant function
      ↓
   dependency only if necessary

8. Never read unrelated files.

9. Before editing, make sure you understand the actual cause.

10. When fixing the problem:
    - Use edit_file.
    - Provide exactly:
        file_path
        old_code
        new_code
    - old_code must exactly match code obtained from read_file.
    - Make the smallest possible change.

11. After editing, read the modified section again to verify the change
    was applied correctly.

12. Do not modify files that are unrelated to the error.

13. If you cannot confidently determine the correct fix, do not guess.
    Explain what information is missing.

14. Do not re-verify a conclusion you can already draw from a file you've
    already read. If, from the file content you already retrieved, a
    variable/function/import is clearly missing or clearly wrong, that is
    sufficient evidence on its own. Do not run additional searches just to
    double-check something you can already see.

15. You have a limited number of tool calls. Prioritize reaching edit_file
    over exhaustive verification. Spend at most one exploratory tool call
    confirming a hypothesis before acting on it.

16. Once you have identified the exact old_code and new_code, call
    edit_file immediately in that same turn. Do not stop and only describe
    the fix in text — a text-only response without calling edit_file is
    an incomplete answer and will be treated as a failure.

Do not modify files unless you have enough evidence that the change fixes
the reported error.
"""

def build_suggest_fix_prompt(error: str, logs: str, description: str, tech_stack: str, file_path: str, file_content: str) -> str:
    return f"""
You are an AI coding assistant. You are given the full content of ONE file
and an error that occurred. Unlike other tools, you do NOT have file-reading
or file-editing tools available — you must determine the fix directly from
the file content given to you below.

ERROR:
{error}

LOGS:
{logs}

DESCRIPTION:
{description}

TECH STACK:
{tech_stack}

FILE PATH:
{file_path}

FILE CONTENT:
{file_content}

INSTRUCTIONS:

1. Determine whether the error can be confidently fixed by editing this file.
2. If yes:
   - old_code must be an exact, verbatim substring of the file content above,
     with exact whitespace/indentation as shown.
   - new_code is the corrected replacement for that exact substring.
   - Make the smallest possible change that fixes the reported error.
3. If you cannot confidently determine the fix from this file alone
   (e.g. the bug is in a different file, or requires information not
   present here), set can_fix to false and explain what's missing in
   explanation. Do not guess.
4. Do not fix unrelated issues in the file — only address the reported error.

Return the structured result.
"""
