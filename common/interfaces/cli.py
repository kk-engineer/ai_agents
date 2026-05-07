import time
import os
from rich.panel import Panel
from common.common_utils.console import get_console
import common.common_utils.spinner   # Add new spinner for progress status
from common.core.agent_logic import call_agent, clear_chat_history

console = get_console()


# CLI Input Loop Logic
def run_cli():
    console.print("[bold cyan]💻 CLI Interface: Active. Type your message below:[/bold cyan]")
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

            # --- CLEAR COMMAND LOGIC ---
            if user_query.lower() in ["clear", "/clear"]:
                clear_chat_history()
                os.system('cls' if os.name == 'nt' else 'clear')
                console.print("[bold green]✨ Chat history cleared![/bold green]")
                continue
            # -------------------------------

            start_time = time.time()

            # 3. Spinner: dots is more reliable than simpleDots in many terminal
            #with console.status("[magenta]Thinking...", spinner="progress_bar"):
            with console.status("[magenta]Thinking...", spinner="dots"):
                output = call_agent(user_query)

            elapsed_time = round(time.time() - start_time, 2)

            console.print(Panel(
                f"[bold white]{output}[/bold white] ",
                title="RoboSathi",
                border_style="blue"
            ))
            console.print(f"⏱️  {elapsed_time}s", style="dim")
            #chat_history.append({"role": "assistant", "content": output})

        except KeyboardInterrupt:
            console.print("\n[bold cyan]Exiting... Bye for now! See you soon.[/bold cyan]")
            break
        except Exception as e:
            console.print(f"\n[bold red]Error:[/bold red] {str(e)}")