from dotenv import load_dotenv
from langchain_groq import ChatGroq
from src.incident_analyzer.tools.read_file import read_file
from src.incident_analyzer.tools.list_file import list_files
from src.incident_analyzer.tools.edit_file import edit_file
from src.incident_analyzer.tools.search_file import search_files
from groq import Groq
import json
import os

load_dotenv()


model3 = ChatGroq(model="openai/gpt-oss-120b", temperature=0)

# Direct Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# tools
tools = [read_file, list_files,search_files,edit_file]

agent_model = model3.bind_tools(tools)

# LangChain models

model3 = ChatGroq(model="openai/gpt-oss-safeguard-20b", temperature=0)


def structured_call(model_name: str, prompt: str, schema: dict, schema_name: str):
    schema["additionalProperties"] = False
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": (
                    "Return the requested information according "
                    "to the provided schema."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": schema_name, "strict": True, "schema": schema},
        },
    )

    content = response.choices[0].message.content

    return json.loads(content)
