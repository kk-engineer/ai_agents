import os
from datetime import datetime
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from common.common_utils.memory import MemoryManager
from common.common_utils.memory_utils import search_memory

def load_md_file(filename):
    path = f"common/config/{filename}"
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
    {soul_context}
    {agent_context}
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
        input_variables=["input", "observation", "chat_history"],
        partial_variables={
            "soul_context": load_md_file("soul.md"),
            "agent_context": load_md_file("agent.md"),
            "user_context": load_md_file("user.md"),
            # "agent_tools": load_md_file("tools.md"),
            #"memory": load_md_file("memory.md"),
            #"current_date": current_date,
        }
    )


# Check if simple prompt and does not need agent for execution
def get_simple_prompt():

    template = """
        ### CONTEXT
        {soul_context}
        {user_context}
        
        ### TASK
        Analyze the User Input.
        
        You must return ONLY ONE of these formats:
        
        1. SIMPLE | <answer>
        - Use this when:
          - the answer already exists in the context above
          - OR it is a greeting OR casual conversation
          - OR a static definition
        - In this case directly answer the user.
        
        2. TOOL
        - Use when tools, terminal, web search, weather, latest news, APIs, files, realtime data,
          system inspection, calculations, or verification are needed.
        
        ### EXAMPLES
        
        User: hi
        Output: SIMPLE | Hey Karan! How are you doing?
        
        User: what is my RAM usage
        Output: TOOL
        
        Chat History:
        {chat_history}
        
        User Input: {input}
        Output:
        """

    # Create the PromptTemplate with partial_variables
    # This "bakes in" the user_query and relevant_memory
    return PromptTemplate(
        template=template,
        input_variables=["input", "chat_history"],
        partial_variables={
            "soul_context": load_md_file("soul.md"),
            "user_context": load_md_file("user.md"),
            # "agent_tools": load_md_file("tools.md"),
            # "memory": load_md_file("memory.md"),
            # "current_date": current_date,
        }
    )


def get_thin_worker_prompt():
    # NO Soul, NO User context, NO History. Just tools.
    template = """
    Answer the following questions as best you can. 
    You have access to the following tools:
    {tools}
    
    Today's Date: {current_date}
    
   Use EXACTLY this format:
    
    Question: the input question you must answer
    Thought: I should determine if I need a tool or can answer directly.
    Action: the action to take, must be one of [{tool_names}]
    Action Input: the specific string input for the tool
    Observation: Actual data returned by the tool.
    ... (can repeat N times)
    Thought: I now know the final answer.
    Final Answer: A detailed answer based EXACTLY on the Observation.
    
    Question: {input}
    Thought: {agent_scratchpad}"""

    return PromptTemplate(
        template=template,
        input_variables=["input", "agent_scratchpad", "tools", "tool_names"],
        partial_variables={
            "current_date": datetime.now().strftime("%A, %B %d, %Y"),
        }
    )