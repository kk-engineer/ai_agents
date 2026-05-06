import time
import os
import platform
from rich.console import Console
from rich.markdown import Markdown
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

# --- ENVIRONMENT FIX ---
if os.name != 'nt' and "TERM" not in os.environ:
    os.environ["TERM"] = "xterm-256color"

# Force terminal true helps with spinner visibility in sub-shells
console = Console(force_terminal=True)

USE_LOCAL_LLAMA_CPP_LLM = True
USE_DUCKDUCKGO = True

def initialize_app():
    llm = get_local_llama_llm() if USE_LOCAL_LLAMA_CPP_LLM else get_cloud_llm()
    web_search = get_duckduckgo_search_tool() if USE_DUCKDUCKGO else get_tavily_tool()
    terminal = get_terminal_tool()
    tools = [web_search, terminal]

    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5
    )
    return agent_executor, llm

def is_simple_query_llm(user_input, model):
    simple_prompt = get_simple_prompt()
    chain = simple_prompt | model | StrOutputParser()
    try:
        response = chain.invoke({"text": user_input})
        res_text = getattr(response, 'content', str(response))
        return res_text.strip().lower().startswith("yes")
    except Exception:
        return False

def main():
    with console.status("[bold green]Loading RoboSathi...", spinner="dots"):
        agent_executor, llm = initialize_app()

    chat_history = []
    os.system('cls' if os.name == 'nt' else 'clear')

    while True:
        try:
            # 1. Colors: Yellow for "You"
            # 2. Spacing: Added \n before prompt to separate turns
            user_query = console.input("\n[bold yellow]You:[/bold yellow] ")

            if user_query.lower() in ["exit", "quit"]:
                break
            if not user_query.strip():
                continue

            chat_history.append({"role": "user", "content": user_query})
            start_time = time.time()

            # 3. Spinner: dots is more reliable than simpleDots in many terminals
            with console.status("[magenta]Thinking...", spinner="dots"):
                history_str = "\n".join([
                    m["content"] for m in chat_history[-3:] if m["role"] == "user"
                ])

                if is_simple_query_llm(user_query, llm):
                    response = llm.invoke(f"The user said '{user_query}'. Give a short, friendly greeting.")
                    output = getattr(response, 'content', str(response))
                else:
                    response = agent_executor.invoke({
                        "input": user_query,
                        "chat_history": history_str
                    })
                    output = response["output"]

            elapsed_time = round(time.time() - start_time, 2)

            # 4. Colors: Green for "RoboSathi"
            console.print("\n[bold blue]RoboSathi:[/bold blue]")
            console.print(Markdown(output))
            console.print(f"⏱️ {elapsed_time}s", style="dim")
            chat_history.append({"role": "assistant", "content": output})

        except KeyboardInterrupt:
            console.print("\n[bold cyan]Exiting... Bye for now! See you soon.[/bold cyan]")
            break
        except Exception as e:
            console.print(f"\n[bold red]Error:[/bold red] {str(e)}")

if __name__ == "__main__":
    main()