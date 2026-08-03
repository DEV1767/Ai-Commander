# Incident Analyzer

A small CLI tool that uses LangGraph and LLMs to analyze pasted error logs and provide:
- extracted error, logs, description, tech stack
- risk analysis (High/Medium/Low)
- explanation and prevention suggestions for non-low risk incidents

This project wires LangGraph state nodes to LLM integrations (Google Generative AI and Groq) to perform structured extraction and suggestions.

Files of interest
- [main.py](C:/Users/Shivam/Desktop/Agent/main.py) - CLI entrypoint. Paste logs when prompted and the graph runs.
- [requirements.txt](C:/Users/Shivam/Desktop/Agent/requirements.txt) - Python dependencies.
- [src/incident_analyzer/](/C:/Users/Shivam/Desktop/Agent/src/incident_analyzer) - core graph, nodes, prompts, and LLM wiring.

Quickstart (Windows)
1. Create a virtual environment and activate it:
   - python -m venv myvenv
   - myvenv\Scripts\activate
2. Install dependencies:
   - pip install -r requirements.txt
3. Create a `.env` file with required credentials for the LLM providers (see the LLM wrappers in `src/incident_analyzer/llm.py`).
4. Run the tool:
   - python main.py
   - Paste your error/logs when prompted and press Enter.

Environment
- Python 3.13+ recommended (this project was validated on 3.13)
- Virtualenv/venv recommended to isolate dependencies

Notes
- The project currently runs as a CLI. A FastAPI integration was added briefly and then removed; the current main.py expects interactive input.
- Add any local data files in a `data/` folder — it's ignored by git via `.gitignore`.

Contributing
- Open an issue or create a PR. Keep changes focused and add tests for new logic where appropriate.

License
- No license specified. Add a LICENSE file if you intend to open source this repository.
