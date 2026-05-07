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
    
    ### LONG-TERM MEMORY (Persistent)
    {persistent_memory}

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
def get_simple_prompt(persistent_memory="No memory available."):
    simple_prompt = ChatPromptTemplate.from_template(
        "### INSTRUCTION\n"
        "You are a router for an AI assistant. Analyze the User Input and categorize it.\n\n"
        "### AVAILABLE CONTEXT (Persistent Memory)\n"
        f"{persistent_memory}\n\n"
        "### CATEGORIES\n"
        "1. 'SIMPLE': The answer is ALREADY present in the Persistent Memory above, OR"
        "it is a Social greetings or general knowledge or a request for a static definition that doesn't need fresh data.\n\n"
        "2. 'MEMORY': If the user explicitly asks to 'remember', 'save', or 'store' something.\n"
        "3. 'TOOL': If the input requires terminal access, web search, or real-time data.\n"
        "### GUARDRAIL 1: DATA FRESHNESS\n"
        "If the input mentions system configuration, weather, or time-sensitive facts (latest, update, news etc.), "
        "you MUST respond 'TOOL'. Your internal training data is considered STALE for these topics.\n\n"
        "### GUARDRAIL 2: THE HALLUCINATION TRAP\n"
        "If the user asks 'What is my [X]?', you DO NOT know the answer. Even if it is in your context, "
        "you MUST select 'TOOL' to verify the current state. Do not rely on static summaries.\n\n"
        "User Input: {text}\n"
        "Response (Output ONLY the word 'SIMPLE', 'TOOL', or 'MEMORY'):"
    )
    return simple_prompt

def get_thin_worker_prompt(persistent_memory="No long-term memory provided."):
    # NO Soul, NO User context, NO History. Just tools.
    template = """Answer the following questions as best you can. 
    Yo have access to below tools :
    {tools}
    
    Today's Date: {current_date}
    
    ### SELECTIVE MEMORY (Relevant Facts)
    {persistent_memory}
    
    STRICT RESPONSE FORMAT:
    Question: the input question you must answer
    Thought: I should determine if I need a tool or can answer directly.
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the specific string input for the tool
    Observation: Actual data returned by the tool.
    ... (can repeat N times)
    Thought: I will now synthesize the Observation into a helpful response.
    Final Answer: A detailed answer based EXACTLY on the Observation.
    
    STRICT RULES:
    1. For terminal tool system configuration, run this multi-command in one action:
    sw_vers -productVersion; system_profiler SPHardwareDataType | grep -E "Model Name|Chip|Memory"; system_profiler SPDisplaysDataType | grep "Chipset Model"; df -H /System/Volumes/Data | head -n 2; 
    system_profiler SPHardwareDataType | grep -E "Total Number of Cores"; system_profiler SPDisplaysDataType | grep -E "Total Number of Cores"
    2. **SELECTIVE MEMORY RULE:** 
       - ONLY use the 'remember_info' tool if the user explicitly asks to 'remember', 'save', or 'store' a fact. 
       - Do not auto-save every conversation.
    3. **INSTALLATION LOCK:** 
    - NEVER run commands to install, download, or update software (e.g., brew, pip, npm, curl, wget) without explicit user permission. 
    If a task requires a new package, ask the user first in a Final Answer.
    
    Question: {input}
    Thought: {agent_scratchpad}"""

    return PromptTemplate(
        template=template,
        input_variables=["input", "agent_scratchpad", "tools", "tool_names"],
        partial_variables={
            "current_date": datetime.now().strftime("%A, %B %d, %Y"),
            "persistent_memory": persistent_memory
        }
    )