from datetime import datetime
import json

from common.common_utils.memory import MemoryManager


# =========================================================
# MEMORY SEARCH
# =========================================================

def search_memory(query: str, memory_text: str):

    query = query.lower().strip()

    best_memory = None
    best_score = 0

    for line in memory_text.splitlines():

        line = line.strip()

        if not line:
            continue

        try:
            memory = json.loads(line)

        except Exception:
            continue

        key = memory.get("key", "").lower().strip()

        score = 0

        # -----------------------------------
        # Exact match
        # -----------------------------------

        if query == key:
            score = 100

        # -----------------------------------
        # Strong containment
        # -----------------------------------

        elif (
            len(query) > 8
            and query in key
        ):

            score = 80

        elif (
            len(key) > 8
            and key in query
        ):

            score = 70

        # -----------------------------------
        # Best match
        # -----------------------------------

        if score > best_score:

            best_score = score
            best_memory = memory

    # -----------------------------------
    # Strict threshold
    # -----------------------------------

    if best_score >= 80:
        return best_memory

    return None


# =========================================================
# GET RELEVANT MEMORY
# =========================================================

def get_relevant_memory(user_query):

    memory_text = MemoryManager.read_memory()

    if not memory_text:
        return None

    relevant_memory = search_memory(
        user_query,
        memory_text
    )

    return relevant_memory


# =========================================================
# SAVE MEMORY
# =========================================================

def remember_info(key: str, value: str) -> str:

    memory_entry = {
        "timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "key": key,
        "value": value
    }

    memory_json = json.dumps(
        memory_entry,
        ensure_ascii=False
    )

    MemoryManager.write_memory(
        memory_json
    )

    return (
        f"Saved to long-term memory:\n"
        f"{key}"
    )


# =========================================================
# UPDATE MEMORY
# =========================================================

def update_memory(messages, current_query):

    if len(messages) < 2:

        print("Nothing saved")

        return "Nothing available to save yet."

    # -----------------------------------
    # Extract what user wants saved
    # -----------------------------------

    save_query = (
        current_query
        .lower()
        .replace("save", "")
        .replace("remember", "")
        .replace("store", "")
        .replace("this", "")
        .replace("it", "")
        .strip()
    )

    best_score = 0
    best_pair = None

    # -----------------------------------
    # Scan backwards through history
    # -----------------------------------

    for i in range(len(messages) - 1, 0, -1):

        current_msg = messages[i]
        prev_msg = messages[i - 1]

        # -----------------------------------
        # Need USER -> ASSISTANT pair
        # -----------------------------------

        if (
            prev_msg["role"] == "user"
            and current_msg["role"] == "assistant"
        ):

            user_text = prev_msg["content"].strip()
            assistant_text = current_msg["content"].strip()

            # -----------------------------------
            # Ignore tiny junk
            # -----------------------------------

            if len(user_text) < 5:
                continue

            if len(assistant_text) < 10:
                continue

            user_lower = user_text.lower()

            score = 0

            # -----------------------------------
            # Exact containment
            # -----------------------------------

            if save_query and save_query in user_lower:
                score += 100

            # -----------------------------------
            # Keyword overlap
            # -----------------------------------

            overlap = (
                set(save_query.split())
                &
                set(user_lower.split())
            )

            score += len(overlap) * 10

            # -----------------------------------
            # Prefer recent relevant matches
            # -----------------------------------

            if score > best_score:

                best_score = score

                best_pair = (
                    user_text,
                    assistant_text
                )

    # -----------------------------------
    # Fallback:
    # Save latest meaningful pair
    # -----------------------------------

    if not best_pair:

        for i in range(len(messages) - 1, 0, -1):

            current_msg = messages[i]
            prev_msg = messages[i - 1]

            if (
                prev_msg["role"] == "user"
                and current_msg["role"] == "assistant"
            ):

                user_text = prev_msg["content"].strip()
                assistant_text = current_msg["content"].strip()

                if (
                    len(user_text) > 5
                    and len(assistant_text) > 10
                ):

                    best_pair = (
                        user_text,
                        assistant_text
                    )

                    break

    # -----------------------------------
    # Nothing useful found
    # -----------------------------------

    if not best_pair:

        print("Nothing saved")

        return (
            "Nothing relevant in chat found to save."
        )

    best_user, best_assistant = best_pair

    # -----------------------------------
    # Skip duplicate memories
    # -----------------------------------

    existing_memory = get_relevant_memory(
        best_user
    )

    if existing_memory:

        print(
            f"Memory already exists -> {best_user}"
        )

        return (
            "This information is already stored."
        )

    # -----------------------------------
    # Save memory
    # -----------------------------------

    print(
        f"SAVING MEMORY -> {best_user}"
    )

    result_message = remember_info(
        key=best_user,
        value=best_assistant
    )

    return result_message


# =========================================================
# TEST
# =========================================================

def main():

    print(
        get_relevant_memory(
            "my system info"
        )
    )


if __name__ == "__main__":
    main()