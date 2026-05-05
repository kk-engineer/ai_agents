from langchain_ollama import ChatOllama

def get_ollama_llm():
    """
    Returns the local Ollama instance.
    """
    return ChatOllama(
        model="gemma4:e4b",
        temperature=0,
        #num_ctx=2048, # Balance between speed and memory for 16GB RAM
        num_thread=4
    )