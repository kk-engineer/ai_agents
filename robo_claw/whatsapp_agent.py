import threading
import time
import os
from neonize.client import NewClient
from neonize.events import MessageEv, ConnectedEv, event
from rich.panel import Panel
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

import logging
# List of noisy loggers to silence
noisy_loggers = ["httpx", "httpcore", "openai", "duckduckgo_search"]
for logger_name in noisy_loggers:
    logging.getLogger(logger_name).setLevel(logging.WARNING)

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

chat_history = []

def call_agent(user_query):
    chat_history.append({"role": "user", "content": user_query})
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

    return output

# 1. Initialize Global Agent
agent_executor, llm = initialize_app()

# 2. WhatsApp Logic
# 'database' parameter ensures QR scan is only needed once
# Pass the session name first; Neonize uses this to create the .db file automatically
client = NewClient("whatsapp_session")

# Agent call logic here
@client.event(ConnectedEv)
def on_connected(client: NewClient, event: ConnectedEv):
    console.print("[bold green]✅ WhatsApp Interface: Connected & Online[/bold green]")

# Initialize a global variable for loop protection
last_sent_response = ""

@client.event(MessageEv)
def on_message(client: NewClient, event: MessageEv):
    global last_sent_response
    info = event.Info

    # 1. FILTER: Ignore all Group messages
    is_group = getattr(info, "IsGroup", getattr(info, "isGroup", False))
    if is_group:
        return

    # 2. DEFINE JID & FILTER: Identify "Self-Chat"
    # Assign sender_jid from the message source to fix the NameError
    sender_jid = info.MessageSource.Chat
    chat_user = sender_jid.User
    sender_user = info.MessageSource.Sender.User

    # Only respond if you are messaging yourself (Notes to Self)
    if chat_user != sender_user:
        return

    # 3. TEXT EXTRACTION
    user_text = ""
    if event.Message.conversation:
        user_text = event.Message.conversation
    elif event.Message.extendedTextMessage and event.Message.extendedTextMessage.text:
        user_text = event.Message.extendedTextMessage.text

    # 4. LOOP PROTECTION
    # If the incoming text is exactly what the bot just sent, ignore it.
    if not user_text or user_text == last_sent_response:
        return

    # 5 EXECUTION
    user_text = ""
    if event.Message.conversation:
        user_text = event.Message.conversation
    elif event.Message.extendedTextMessage and event.Message.extendedTextMessage.text:
        user_text = event.Message.extendedTextMessage.text

    if user_text:
        # LOG TO CLI
        console.print(Panel(
            f"[bold green]WhatsApp In ({sender_jid.User}):[/bold green] {user_text}",
            title="WhatsApp Message",
            border_style="green"
        ))

        try:
            output = call_agent(user_text)

            # Reply via WhatsApp
            client.send_message(sender_jid, output)

            # LOG REPLY TO CLI
            console.print(Panel(
                f"[bold blue]WhatsApp Out to {sender_jid.User}:[/bold blue] {output}",
                title="Agent Response",
                border_style="blue"
            ))
        except Exception as e:
            console.print(f"[bold red]Error in WhatsApp Agent: {e}[/bold red]")

# 3. CLI Input Loop Logic
def run_cli():
    console.print("[bold cyan]💻 CLI Interface: Active. Type your message below:[/bold cyan]")
    with console.status("[bold green]Loading RoboSathi...", spinner="dots"):
        agent_executor, llm = initialize_app()


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

            start_time = time.time()

            # 3. Spinner: dots is more reliable than simpleDots in many terminals
            with console.status("[magenta]Thinking...", spinner="dots"):
                output = call_agent(user_query)

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


# 4. Orchestration
def main():
    # Start WhatsApp in a background thread
    wa_thread = threading.Thread(target=client.connect, daemon=True)
    wa_thread.start()

    # Give WhatsApp a moment to initialize/display QR if needed
    time.sleep(2)

    # Start CLI in the foreground
    run_cli()


if __name__ == "__main__":
    main()