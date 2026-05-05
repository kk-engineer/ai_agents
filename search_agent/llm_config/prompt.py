import os
from datetime import datetime
from langchain_core.prompts import PromptTemplate

def load_md_file(filename):
    path = f"config/{filename}"
    if os.path.exists(path):
        with open(path, "r") as f:
            # We escape any existing curly braces in your markdown files
            # so they don't break the LangChain parser
            return f.read().replace("{", "{{").replace("}", "}}")
    return "No context provided."

def get_agent_prompt():
    current_date = datetime.now().strftime("%A, %B %d, %Y")

    # 1. Define the RAW template string (NO f-string here)
    # We use single braces {input} for things LangChain must fill later
    template = """
{soul}
{agent_rules}
{user_context}

Answer the user's question using the following tools:
{tools}

STRICT RESPONSE FORMAT:
Question: {input}
Thought: I should determine if I need a tool or can answer directly.
Action: [{tool_names}] (ONLY if needed)
Action Input: [input] (ONLY if needed)
Observation: [tool_output]
... (repeat if needed)
Thought: I now have the answer.
Final Answer: [your final response to the user]

EXAMPLES OF CORRECT FORMAT:
Question: Hi
Thought: The user is greeting me. I don't need a tool.
Final Answer: Hello! I am RoboSathi, your AI assistant. How can I help you today?

Question: Weather in Pune?
Thought: I need real-time data. I will use the search tool.
Action: duckduckgo_search
Action Input: weather in Pune
Observation: Current temperature in Pune is 31°C and sunny.
Thought: I have the information needed to answer.
Final Answer: The current weather in Pune is 31°C and sunny.

Today's Date: {current_date}
Memory: {memory}

Chat History:
{chat_history}

Question: {input}
Thought: {agent_scratchpad}"""

    # 2. Create the PromptTemplate with partial_variables
    # This "bakes in" the file content and date so you don't need to pass them in main.py
    return PromptTemplate(
        template=template,
        input_variables=["input", "chat_history", "agent_scratchpad", "tools", "tool_names"],
        partial_variables={
            "soul": load_md_file("soul.md"),
            "agent_rules": load_md_file("agent.md"),
            "user_context": load_md_file("user.md"),
            "memory": load_md_file("memory.md"),
            "current_date": current_date,
        }
    )

prompt = get_agent_prompt()