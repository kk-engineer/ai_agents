import threading
import time
import logging
# Local imports
from interfaces.cli import run_cli
from interfaces.whatsapp import get_whatsApp_client

from langchain_core.globals import set_debug

#set_debug(True)

# List of noisy loggers to silence
noisy_loggers = ["httpx", "httpcore", "duckduckgo_search", "whatsmeow"]
for logger_name in noisy_loggers:
    logging.getLogger(logger_name).setLevel(logging.WARNING)

# Orchestration
def main():
    # Start WhatsApp in a background thread
    wa_thread = threading.Thread(target=get_whatsApp_client().connect, daemon=True)
    wa_thread.start()

    # Give WhatsApp a moment to initialize/display QR if needed
    time.sleep(2)

    # Start CLI in the foreground
    run_cli()

if __name__ == "__main__":
    main()