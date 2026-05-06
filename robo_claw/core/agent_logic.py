from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import Tool

# Local imports
from llm_config.local_llama_cpp import get_local_llama_llm
from llm_config.online_llm import get_cloud_llm
from tools.search_duckduckgo import get_duckduckgo_search_tool
from tools.search_tavily import get_tavily_tool
from tools.terminal_tool import get_terminal_tool
from tools.memory_tool import remember_info  # The function that calls MemoryManager.write_memory()

from robo_utils.chat_manager import get_chat_manager
from robo_utils.clean_tool_output import clean_web_search_output, clean_terminal_output
from robo_utils.memory import MemoryManager
from llm_config.prompt import get_synthesis_prompt, get_thin_worker_prompt, get_simple_prompt

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
        ),
        Tool(
            name="remember_info",
            func=remember_info,
            description="MANDATORY for saving facts. Use when the user says 'remember this' or 'save to memory'."
        )
    ]


def call_agent(user_query):
    llm = get_llm()
    tools = get_tools()

    # --- STAGE 1: THE INTEGRATED ROUTER ---
    # PRE-FETCH Memory for the Router
    current_memory = MemoryManager.read_memory()
    router_chain = get_simple_prompt(persistent_memory=current_memory) | llm | StrOutputParser()
    decision = router_chain.invoke({"text": user_query}).strip().upper()

    # --- STAGE 2: FAST-TRACK MEMORY (Bypass Agent & Synthesis) ---
    if decision == "MEMORY":
        messages = chat_manager.get_messages()

        # We isolate the specific pair that needs saving
        original_user_intent = "Unknown Topic"
        actual_agent_response = "No data found"

        if len(messages) >= 2:
            # The message that provided the facts (last turn)
            actual_agent_response = messages[-1]['content']
            # The message that asked for the facts (last turn)
            original_user_intent = messages[-2]['content']

        # 1. Create a focused extraction context
        focused_context = (
            f"Question: {original_user_intent}\n"
            f"Answer: {actual_agent_response}"
        )

        # 2. Sharpen the extraction prompt to bridge ONLY these two points
        extraction_prompt = (
            "TASK: Summarize the following exchange into a single 'Topic: Fact' entry for a permanent log.\n"
            f"EXCHANGE:\n{focused_context}\n\n"
            "REQUIREMENTS:\n"
            "1. The 'Topic' must reflect the Question (e.g., System config).\n"
            "2. The 'Fact' must contain the specific data from the Answer.\n"
            "3. Format: [Topic]: [Data]\n"
            "4. Output ONLY the formatted pair."
        )

        # Invoke LLM to get the actual details
        extracted_fact = llm.invoke(extraction_prompt).content.strip()

        # Persist to config/memory.md
        result_message = remember_info(extracted_fact)

        # Update Chat History
        chat_manager.add_message("user", user_query)
        chat_manager.add_message("assistant", result_message)
        return result_message

    # --- STAGE 3: AGENT CALL (Only if TOOL is needed) ---
    observation = ""
    if decision == "TOOL":
        current_memory = MemoryManager.read_memory()
        thin_prompt = get_thin_worker_prompt(persistent_memory=current_memory)

        thin_agent = create_react_agent(llm, tools, thin_prompt)
        executor = AgentExecutor(
            agent=thin_agent,
            tools=tools,
            handle_parsing_errors=True,
            max_iterations=2,  # Critical for 16GB RAM limit
            verbose=True
        )

        worker_result = executor.invoke({"input": user_query})
        observation = worker_result["output"]

    # --- STAGE 4: DIRECT SYNTHESIS (Persona Delivery) ---
    synthesis_prompt = get_synthesis_prompt()
    synthesis_chain = synthesis_prompt | llm | StrOutputParser()

    final_output = synthesis_chain.invoke({
        "input": user_query,
        "observation": observation,
        "chat_history": chat_manager.get_as_string(),
        "persistent_memory": MemoryManager.read_memory()
    })

    # Update History for next turn
    chat_manager.add_message("user", user_query)
    chat_manager.add_message("assistant", final_output)

    return final_output


def clear_chat_history():
    chat_manager.clear()