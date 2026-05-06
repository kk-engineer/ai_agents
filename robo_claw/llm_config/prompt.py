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

def get_synthesis_prompt():
    # 1. Define the RAW template string (NO f-string here)
    # We use single braces {input} for things LangChain must fill later
    template = """
    {soul}
    {agent_rules}
    {user_context}
        
    The assistant has gathered the following information to answer the user's request:
    {observation}
    
    Chat History:
    {chat_history}

    User Question: {input}
    
    Based on the information above and your unique persona, provide a final, direct answer to the user. 
    Do not include "Thought" or "Action" steps. Just speak naturally.
    """

    # 2. Create the PromptTemplate with partial_variables
    # This "bakes in" the file content and date so you don't need to pass them in main.py
    return PromptTemplate(
        template=template,
        input_variables=["input", "chat_history", "observation"],
        partial_variables={
            "soul": load_md_file("soul.md"),
            "agent_rules": load_md_file("agent.md"),
            "user_context": load_md_file("user.md"),
            # "agent_tools": load_md_file("tools.md"),
            #"memory": load_md_file("memory.md"),
            #"current_date": current_date,
        }
    )


# Check if simple prompt and does not need agent for execution
def get_simple_prompt():
    simple_prompt = ChatPromptTemplate.from_template(
        "Analyze the user input and categorize it into ONE of two categories:\n\n"
        "1. SIMPLE: Greetings, identity questions, gratitude, or general knowledge that "
        "DOES NOT require searching the web or checking the local system/terminal.\n"
        "2. TOOL: Requests that require current weather, news, web searches, "
        "running terminal commands, checking system specs, or file operations.\n\n"
        "User Input: {text}\n\n"
        "Respond with ONLY the word 'SIMPLE' or 'TOOL'."
    )
    return simple_prompt

def get_thin_worker_prompt():
    # NO Soul, NO User context, NO History. Just tools.
    template = """Answer the following questions as best you can. 
    Yo have access to below tools :
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

    
    Question: {input}
    Thought: {agent_scratchpad}"""

    return PromptTemplate(
        template=template,
        input_variables=["input", "agent_scratchpad", "tools", "tool_names"],
        partial_variables={
            "current_date": datetime.now().strftime("%A, %B %d, %Y")
        }
    )