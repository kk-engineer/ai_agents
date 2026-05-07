from neonize.client import NewClient
from neonize.events import MessageEv, ConnectedEv, event
from rich.panel import Panel
import time

# Local imports
from common.common_utils.console import get_console
from common.core.agent_logic import call_agent

console = get_console()

# WhatsApp Logic
# 'database' parameter ensures QR scan is only needed once
# Pass the session name first; Neonize uses this to create the .db file automatically
client = NewClient("whatsapp_session")

def get_whatsApp_client():
    return client

# Agent call logic here
@client.event(ConnectedEv)
def on_connected(client: NewClient, event: ConnectedEv):
    console.print("[bold green]✅ WhatsApp Interface: Connected & Online[/bold green]")

# Initialize a global variable for loop protection
last_sent_response = ""

@client.event(MessageEv)
def on_message(client: NewClient, event: MessageEv):
    start_time = time.time()
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
                title="RoboSathi",
                border_style="blue"
            ))
            elapsed_time = round(time.time() - start_time, 2)
            console.print(f"⏱️ {elapsed_time}s", style="dim")

        except Exception as e:
            console.print(f"[bold red]Error in WhatsApp Agent: {e}[/bold red]")