import re

def clean_web_search_output(raw_output: str) -> str:
    """
    Cleans messy search results by extracting only titles and snippets.
    This reduces the 'reasoning tax' on the LLM.
    """
    # If the output is a string of results, we want to make it structured
    # but concise. We remove URLs and metadata that confuse smaller models.
    lines = raw_output.split('\n')
    cleaned_lines = []
    for line in lines:
        if "http" in line:  # Optional: Strip links if you just want facts
            line = line.split("http")[0]
        cleaned_lines.append(line.strip())

    return "\n".join([l for l in cleaned_lines if l])


def clean_terminal_output(raw_output: str, max_lines: int = 20) -> str:
    """
    Cleans and truncates terminal output for LLM consumption.
    1. Removes ANSI escape codes (colors/formatting).
    2. Truncates long outputs to prevent context overflow.
    3. Removes empty lines or repetitive prompt markers.
    """
    # 1. Strip ANSI escape codes (colors, bold, etc.)
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    clean_text = ansi_escape.sub('', raw_output)

    # 2. Split into lines and filter
    lines = [line.strip() for line in clean_text.split('\n') if line.strip()]

    # 3. Intelligent Truncation
    if len(lines) > max_lines:
        first_half = lines[:max_lines // 2]
        last_half = lines[-max_lines // 2:]
        return "\n".join(first_half + ["... [Output Truncated for Brevity] ..."] + last_half)

    return "\n".join(lines)