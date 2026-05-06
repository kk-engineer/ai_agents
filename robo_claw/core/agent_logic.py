from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.output_parsers import StrOutputParser

# Local imports
from llm_config.local_llm import get_ollama_llm
from llm_config.online_llm import get_cloud_llm
from llm_config.local_llama_cpp import get_local_llama_llm
from llm_config.prompt import prompt
from llm_config.prompt import get_simple_prompt
from tools.search_duckduckgo import get_duckduckgo_search_tool
from tools.search_tavily import get_tavily_tool
from tools.terminal_tool import get_terminal_tool


USE_LOCAL_LLAMA_CPP_LLM = True
USE_DUCKDUCKGO = True

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
        max_iterations=2
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
    chat_history.append({"role": "user", "content": user_query})
    history_str = "\n".join([
        m["content"] for m in chat_history[-3:] if m["role"] == "user"
    ])

    if is_simple_query_llm(user_query):
        response = get_llm().invoke(f"The user said '{user_query}'. Give a short, friendly greeting.")
        output = getattr(response, 'content', str(response))
    else:
        response = get_agent_executor().invoke({
            "input": user_query,
            "chat_history": history_str
        })
        output = response["output"]

    return output
