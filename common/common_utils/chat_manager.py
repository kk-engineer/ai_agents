from collections import deque

class ChatManager:
    def __init__(self, max_turns=5):
        # max_turns=4 means 4 User + 4 Assistant messages = 8 total
        self.history = deque(maxlen=max_turns * 2)

    def add_message(self, role, content):
        self.history.append({"role": role, "content": content})

    def get_messages(self):
        """Returns the history as a standard list of dictionaries."""
        return list(self.history)

    def get_as_string(self):
        # Formats for the Chat History section of your prompt
        return "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in self.history])

    def clear(self):
        self.history.clear()

# Initialize once
def get_chat_manager():
    return ChatManager()