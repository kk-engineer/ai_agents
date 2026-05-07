import os
from datetime import datetime

MEMORY_FILE = os.path.join("config", "memory.md")


class MemoryManager:
    @staticmethod
    def read_memory() -> str:
        # Ensure the config directory exists
        if not os.path.exists("config"):
            os.makedirs("config")

        if not os.path.exists(MEMORY_FILE):
            return "No prior long-term memory stored."

        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            return content if content else "Memory is currently empty."

    @staticmethod
    def write_memory(content: str):
        if not os.path.exists("config"):
            os.makedirs("config")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = f"\n- [{timestamp}] {content}"

        with open(MEMORY_FILE, "a", encoding="utf-8") as f:
            f.write(entry)