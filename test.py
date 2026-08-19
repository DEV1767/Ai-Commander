from src.incident_analyzer.nodes import action_node

state = {
    "error": "ReferenceError: userData is not defined",
    "logs": "ReferenceError: userData is not defined at login.js:42",
    "description": "Login crashes when submitting the login form.",
    "tech_stack": "JavaScript",
}


result = action_node(state)


print("\n==============================")
print("ACTION RESPONSE")
print("==============================")
print(result.get("action_response"))


print("\n==============================")
print("TOOLS USED")
print("==============================")
print(result.get("tool_used"))
