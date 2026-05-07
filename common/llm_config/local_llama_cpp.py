from langchain_openai import ChatOpenAI

def get_local_llama_llm():
    return ChatOpenAI(
        base_url="http://localhost:8000/v1",
        api_key="sk-no-key-required",
        temperature=1.9,
        top_p=0.95,
        presence_penalty=2.0,  # Higher penalty to break the "shouting" loop
        frequency_penalty=2.0, # Punishes repetitive token
    )