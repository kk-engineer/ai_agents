from tabnanny import verbose

from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.output_parsers import StrOutputParser

# Local imports
from llm_config.local_llm import get_ollama_llm
from llm_config.online_llm import get_cloud_llm
from llm_config.local_llama_cpp import get_local_llama_llm
from tools.search_duckduckgo import get_duckduckgo_search_tool
from tools.search_tavily import get_tavily_tool
from tools.terminal_tool import get_terminal_tool
from robo_utils.chat_manager import get_chat_manager
from llm_config.prompt import get_synthesis_prompt, get_thin_worker_prompt, get_simple_prompt


USE_LOCAL_LLAMA_CPP_LLM = True
USE_DUCKDUCKGO = False

chat_manager = get_chat_manager()

def get_llm():
    llm = get_local_llama_llm() if USE_LOCAL_LLAMA_CPP_LLM else get_cloud_llm()
    return llm

def get_tools():
    web_search = get_duckduckgo_search_tool() if USE_DUCKDUCKGO else get_tavily_tool()
    terminal = get_terminal_tool()
    tools = [web_search, terminal]
    return tools

def get_agent_executor():
    tools = get_tools()
    agent = create_react_agent(get_llm(), tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5
    )
    return agent_executor

def is_simple_query_llm(user_input):
    llm = get_llm()
    simple_prompt = get_simple_prompt()
    chain = simple_prompt | llm | StrOutputParser()
    try:
        response = chain.invoke({"text": user_input})
        res_text = getattr(response, 'content', str(response))
        return res_text.strip().lower().startswith("yes")
    except Exception:
        return False

chat_history = []


def call_agent(user_query):
    llm = get_llm()
    tools = get_tools()

    # --- STAGE 1: THE INTEGRATED ROUTER ---
    router_chain = get_simple_prompt() | llm | StrOutputParser()
    decision = router_chain.invoke({"text": user_query}).strip().upper()

    observation = ""

    # --- STAGE 2: AGENT CALL (Only if TOOL is needed) ---
    if "TOOL" in decision:
        thin_prompt = get_thin_worker_prompt()
        thin_agent = create_react_agent(llm, tools, thin_prompt)
        executor = AgentExecutor(
            agent=thin_agent,
            tools=tools,
            handle_parsing_errors=True,
            max_iterations=3,
            verbose=True)

        # This gets the raw data
        worker_result = executor.invoke({"input": user_query})
        observation = worker_result["output"]

    # 3. DIRECT SYNTHESIS (Persona Delivery)
    # We switch to a standard LLM chain, NOT an AgentExecutor
    synthesis_prompt = get_synthesis_prompt()
    synthesis_chain = synthesis_prompt | llm | StrOutputParser()

    # This call is significantly faster because the LLM isn't
    # trying to format complex Action/Observation blocks.
    final_output = synthesis_chain.invoke({
        "input": user_query,
        "observation": observation,
        "chat_history": chat_manager.get_as_string()
    })

    # 4. Save to history
    chat_manager.add_message("user", user_query)
    chat_manager.add_message("assistant", final_output)

    return final_output

def clear_chat_history():
    chat_manager.clear()