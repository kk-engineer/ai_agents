from langchain_ollama import ChatOllama

def get_ollama_llm():
    """
    Returns the local Ollama instance.
    Gemma 4:e4b is chosen for its superior tool-calling and context window.
    """
    return ChatOllama(
        model="gemma4:e4b",
        temperature=0,
        #num_ctx=8192, # Balance between speed and memory for 16GB RAM
    )