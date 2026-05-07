import time

from neonize.client import NewClient
from neonize.events import MessageEv, ConnectedEv
from rich.panel import Panel

# Local imports
from common.common_utils.console import get_console
from common.core.agent_logic import call_agent

console = get_console()

# -----------------------------------
# WHATSAPP CLIENT
# -----------------------------------

client = NewClient("whatsapp_session")


def get_whatsApp_client():
    return client


# -----------------------------------
# RUNTIME SELF ID
# -----------------------------------

SELF_ID = None

# Prevent infinite loops
last_sent_response = ""


# -----------------------------------
# CONNECTED EVENT
# -----------------------------------

@client.event(ConnectedEv)
def on_connected(client: NewClient, event: ConnectedEv):

    console.print(
        "[bold green]✅ WhatsApp Interface Connected[/bold green]"
    )


# -----------------------------------
# MESSAGE EVENT
# -----------------------------------

@client.event(MessageEv)
def on_message(client: NewClient, event: MessageEv):

    global SELF_ID
    global last_sent_response

    start_time = time.time()

    try:

        info = event.Info
        source = info.MessageSource

        # -----------------------------------
        # IGNORE GROUPS
        # -----------------------------------

        is_group = getattr(
            info,
            "IsGroup",
            getattr(info, "isGroup", False)
        )

        if is_group:
            return

        # -----------------------------------
        # EXTRACT IDS
        # -----------------------------------

        chat_user = str(
            getattr(source.Chat, "User", "")
        )

        sender_user = str(
            getattr(source.Sender, "User", "")
        )

        from_me = getattr(
            info,
            "FromMe",
            getattr(info, "fromMe", False)
        )

        # -----------------------------------
        # LEARN SELF ID AUTOMATICALLY
        # -----------------------------------

        # Self-chat uniquely satisfies:
        # chat_user == sender_user

        if SELF_ID is None:

            if (
                chat_user
                and sender_user
                and chat_user == sender_user
            ):

                SELF_ID = chat_user

                console.print(
                    f"[bold cyan]Learned SELF_ID:[/bold cyan] {SELF_ID}"
                )

        # -----------------------------------
        # DEBUG LOGS
        # -----------------------------------

        # console.print({
        #     "chat_user": chat_user,
        #     "sender_user": sender_user,
        #     "from_me": from_me,
        #     "SELF_ID": SELF_ID,
        # })

        # -----------------------------------
        # IGNORE UNTIL SELF_ID FOUND
        # -----------------------------------

        if SELF_ID is None:
            return

        # -----------------------------------
        # ONLY RESPOND TO SELF CHAT
        # -----------------------------------

        is_self_chat = (
            chat_user == SELF_ID
            and sender_user == SELF_ID
        )

        if not is_self_chat:
            return

        # -----------------------------------
        # EXTRACT TEXT
        # -----------------------------------

        user_text = ""

        if getattr(event.Message, "conversation", None):
            user_text = event.Message.conversation

        elif (
            getattr(
                event.Message,
                "extendedTextMessage",
                None
            )
            and event.Message.extendedTextMessage.text
        ):
            user_text = (
                event.Message
                .extendedTextMessage
                .text
            )

        user_text = user_text.strip()

        if not user_text:
            return

        # -----------------------------------
        # LOOP PROTECTION
        # -----------------------------------

        if user_text == last_sent_response:
            return

        # -----------------------------------
        # LOG INPUT
        # -----------------------------------

        console.print(
            Panel(
                f"[bold green]WhatsApp In:[/bold green] {user_text}",
                title="WhatsApp Message",
                border_style="green",
            )
        )

        # -----------------------------------
        # CALL AGENT
        # -----------------------------------

        output = call_agent(user_text)

        if not output:
            return

        output = str(output).strip()

        # Save before sending
        last_sent_response = output

        # -----------------------------------
        # SEND REPLY
        # -----------------------------------

        client.send_message(
            source.Chat,
            output
        )

        # -----------------------------------
        # LOG OUTPUT
        # -----------------------------------

        console.print(
            Panel(
                f"[bold blue]WhatsApp Out:[/bold blue] {output}",
                title="RoboSathi",
                border_style="blue",
            )
        )

        elapsed_time = round(
            time.time() - start_time,
            2
        )

        console.print(
            f"⏱️ {elapsed_time}s",
            style="dim"
        )

    except Exception as e:

        console.print(
            f"[bold red]WhatsApp Error:[/bold red] {e}"
        )