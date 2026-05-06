import os
from langchain_tavily import TavilySearch


def get_tavily_tool():
    # 1. Try to get key from os.environ
    api_key = os.getenv("tavily_api_key")

    if not api_key:
        raise ValueError("Tavily API Key not found. Please check your .env file or export the variable.")

    # 2. Pass the key explicitly to the tool
    tool = TavilySearch(
        tavily_api_key=api_key,  # Passing explicitly fixes the Pydantic error
        max_results=3,
        include_answer=True
    )

    tool.name = "web_search"
    tool.description = (
        "A search engine optimized for comprehensive, accurate, and real-time results. "
        "Use this for any questions about current events, news, general knowledge, "
        "or technical documentation that is NOT on the local machine."
    )
    return tool