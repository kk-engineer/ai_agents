import json

from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import Tool

from common.common_utils.memory_utils import get_relevant_memory, update_memory
from common.core.pre_process import has_relevant_memory, is_memory_save_request
# Local imports
from common.llm_config.local_llama_cpp import get_local_llama_llm
from common.llm_config.online_llm import get_cloud_llm
from common.tools.search_duckduckgo import get_duckduckgo_search_tool
from common.tools.search_tavily import get_tavily_tool
from common.tools.terminal_tool import get_terminal_tool
from common.common_utils.chat_manager import get_chat_manager
from common.common_utils.clean_tool_output import clean_web_search_output, clean_terminal_output
from common.llm_config.prompt import get_synthesis_prompt, get_thin_worker_prompt, get_simple_prompt

USE_LOCAL_LLAMA_CPP_LLM = True
USE_DUCKDUCKGO = True

chat_manager = get_chat_manager()


def get_llm():
    return get_local_llama_llm() if USE_LOCAL_LLAMA_CPP_LLM else get_cloud_llm()


def get_tools():
    raw_web_search = get_duckduckgo_search_tool() if USE_DUCKDUCKGO else get_tavily_tool()
    raw_terminal = get_terminal_tool()

    return [
        Tool(
            name="terminal",
            func=lambda q: clean_terminal_output(raw_terminal.run(q)),
            description="Run terminal commands on this Mac. Use for system config, files, or hardware."
        ),
        Tool(
            name="web_search",
            func=lambda q: clean_web_search_output(raw_web_search.run(q)),
            description="Search the web for general knowledge, news, and weather."
        )
    ]


def call_agent(user_query):
    llm = get_llm()
    tools = get_tools()
    memory_hit = has_relevant_memory(user_query)

    if memory_hit:
        #print("Info already present in memory; No need to call agent!")
        return memory_hit["value"]

    # Check for save to memory request
    if is_memory_save_request(user_query):
        messages = chat_manager.get_messages()
        result_message = update_memory(messages,current_query=user_query)

        chat_manager.add_message("user", user_query)
        chat_manager.add_message("assistant", result_message)

        return result_message

    # --- STAGE 1: THE INTEGRATED ROUTER ---
    router_chain = get_simple_prompt() | llm | StrOutputParser()
    decision = router_chain.invoke({
        "input": user_query,
        "chat_history": chat_manager.get_as_string()
    }).strip()
    #print(decision)

    if decision.startswith("SIMPLE"):
        # Extract the response and print it directly
        final_text = decision.split("|")[1].strip()
        return final_text # Stop here! No second LLM call needed.

    # --- AGENT CALL (Only if TOOL is needed) ---
    observation = ""
    if decision.startswith("TOOL"):
        thin_prompt = get_thin_worker_prompt()

        # Create ReAct LLM
        react_llm = llm.bind(
            stop=["Observation:"]
        )

        thin_agent = create_react_agent(react_llm, tools, thin_prompt)
        executor = AgentExecutor(
            agent=thin_agent,
            tools=tools,
            handle_parsing_errors=True,
            max_iterations=3,
            verbose=True
        )

        worker_result = executor.invoke(
            {"input": user_query,
         })
        observation = worker_result["output"]

    # --- STAGE 4: DIRECT SYNTHESIS (Persona Delivery) ---
    synthesis_prompt = get_synthesis_prompt()
    synthesis_chain = synthesis_prompt | llm | StrOutputParser()

    final_output = synthesis_chain.invoke({
        "input": user_query,
        "observation": observation,
        "chat_history": chat_manager.get_as_string()
    })

    # Update History for next turn
    chat_manager.add_message("user", user_query)
    chat_manager.add_message("assistant", final_output)

    return final_output


def clear_chat_history():
    chat_manager.clear()