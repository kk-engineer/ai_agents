from langchain_openai import ChatOpenAI

def get_local_llama_llm():
    return ChatOpenAI(
        # This talks to your llama.cpp server terminal
        base_url="http://localhost:8000/v1",
        api_key="sk-no-key-required"
    )