import re


def clean_web_search_output(raw_output) -> str:
    """
    Cleans messy search results by extracting only titles and snippets.
    Ensures output is ALWAYS a string to prevent AgentExecutor crashes.
    """
    # 1. Handle non-string inputs (dicts/lists) from search tools
    if isinstance(raw_output, list):
        # Convert list of results into a single string
        processed_output = "\n".join([str(item) for item in raw_output])
    elif isinstance(raw_output, dict):
        # Extract values if it's a single result dictionary
        processed_output = str(raw_output)
    else:
        processed_output = str(raw_output)

    # 2. Clean the string
    lines = processed_output.split('\n')
    cleaned_lines = []
    for line in lines:
        # Strip links to reduce token count and 'reasoning tax'
        if "http" in line:
            line = line.split("http")[0]
        cleaned_lines.append(line.strip())

    return "\n".join([l for l in cleaned_lines if l])


def clean_terminal_output(raw_output, max_lines: int = 20) -> str:
    """
    Cleans and truncates terminal output for LLM consumption.
    Ensures output is ALWAYS a string.
    """
    # Force conversion to string in case of unexpected types
    text_input = str(raw_output)

    # 1. Strip ANSI escape codes (colors, bold, etc.)
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    clean_text = ansi_escape.sub('', text_input)

    # 2. Split into lines and filter
    lines = [line.strip() for line in clean_text.split('\n') if line.strip()]

    # 3. Intelligent Truncation
    if len(lines) > max_lines:
        first_half = lines[:max_lines // 2]
        last_half = lines[-max_lines // 2:]
        return "\n".join(first_half + ["... [Output Truncated] ..."] + last_half)

    return "\n".join(lines)