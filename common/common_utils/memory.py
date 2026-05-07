import os

# =========================================================
# Absolute project-safe path
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MEMORY_FILE = os.path.join(
    BASE_DIR,
    "config",
    "memory.jsonl"
)


class MemoryManager:

    @staticmethod
    def read_memory() -> str | None:

        if not os.path.exists(MEMORY_FILE):

            print(
                f"ERROR: Memory file does not exist -> {MEMORY_FILE}"
            )

            return None

        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return f.read().strip()

    @staticmethod
    def write_memory(content: str):

        # Ensure config directory exists
        os.makedirs(
            os.path.dirname(MEMORY_FILE),
            exist_ok=True
        )

        # Create empty file if missing
        if not os.path.exists(MEMORY_FILE):

            with open(
                MEMORY_FILE,
                "w",
                encoding="utf-8"
            ) as f:
                pass

            print(
                f"Created memory file -> {MEMORY_FILE}"
            )

        # Append JSONL entry
        with open(
            MEMORY_FILE,
            "a",
            encoding="utf-8"
        ) as f:

            f.write(content.strip() + "\n")