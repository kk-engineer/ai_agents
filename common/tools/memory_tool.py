from common.common_utils.memory import MemoryManager


def remember_info(content: str) -> str:
    """
    Saves important information to long-term memory.
    ONLY use this tool if the user explicitly asks you to 'remember',
    'save', or 'store' something for future sessions.
    """
    MemoryManager.write_memory(content)
    return f"I have committed this to my long-term memory: {content}"