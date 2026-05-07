from common.common_utils.memory_utils import get_relevant_memory


def has_relevant_memory(user_query):
    relevant_memory = get_relevant_memory(user_query)
    return relevant_memory

def is_memory_save_request(user_query):
    SAVE_KEYWORDS = [
        "save",
        "remember",
        "store"
    ]

    query = user_query.lower().strip()

    return any(
        query.startswith(keyword)
        for keyword in SAVE_KEYWORDS
    )

def is_reminder_request(user_query):
    REMINDER_KEYWORDS = [
        "remind me",
        "set reminder",
        "add reminder"
    ]

    query = user_query.lower().strip()

    return any(
        query.startswith(keyword)
        for keyword in REMINDER_KEYWORDS
    )