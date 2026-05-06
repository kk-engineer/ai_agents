import os
from datetime import datetime
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate

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

Today's Date: {current_date}

STRICT RESPONSE FORMAT:
Question: the input question you must answer
Thought: I should determine if I need a tool or can answer directly.
Action: the action to take, should be one of [{tool_names}]
Action Input: the specific string input for the tool
Observation: Actual data returned by the tool.
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I will now synthesize the Observation into a helpful response.
Final Answer: A detailed answer based EXACTLY on the Observation.

STRICT RULES:
1. 1. **INSTALLATION LOCK:** NEVER run commands to install, download, or update software (e.g., brew, pip, npm, curl, wget) without explicit user permission. 
If a task requires a new package, ask the user first in a Final Answer.
2. For system configuration run this multi-command in one action:
sw_vers -productVersion; system_profiler SPHardwareDataType | grep -E "Model Name|Chip|Memory"; system_profiler SPDisplaysDataType | grep "Chipset Model"; df -H /System/Volumes/Data | head -n 2; 
system_profiler SPHardwareDataType | grep -E "Total Number of Cores"; system_profiler SPDisplaysDataType | grep -E "Total Number of Cores"

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
            #"agent_tools": load_md_file("tools.md"),
            "user_context": load_md_file("user.md"),
            #"memory": load_md_file("memory.md"),
            "current_date": current_date,
        }
    )

prompt = get_agent_prompt()

# Check if simple prompt and does not need agent for execution
def get_simple_prompt():
    simple_prompt = ChatPromptTemplate.from_template(
        "Determine if the user's input is a simple conversational interaction "
        "that can be answered directly without using any external tools, data, or complex reasoning.\n\n"
        "This includes:\n"
        "- Greetings (e.g., 'hi', 'hello', 'what's up')\n"
        "- Identity questions (e.g., 'who are you', 'what is your name')\n"
        "- Small talk and fillers (e.g., 'how are you', 'cool', 'okay')\n"
        "- Gratitude/Closing (e.g., 'thanks', 'bye')\n\n"
        "Answer 'Yes' if it is a simple interaction. Answer 'No' if it is a task, "
        "a request for information, or requires a tool.\n\n"
        "If the user input contains a command that looks like code or a terminal instruction, always answer No.\n"
        "User Input: {text}\n"
        "Answer (Yes/No):"
    )

    return simple_prompt