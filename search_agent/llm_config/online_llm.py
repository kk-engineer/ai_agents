import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda

def get_cloud_llm():
    """
    Initializes Gemini as primary with OpenRouter as a fallback.
    """
    # Primary: Google Gemini 3 Flash
    secondary_model = ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",
        google_api_key=os.getenv("gemini_api_key"),
        temperature=0,
    )

    # Fallback: OpenRouter (DeepSeek or similar)
    primary_model = ChatOpenAI(
        model="openrouter/free",
        openai_api_key=os.getenv("openrouter_api_key"),
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0,
    )

    # Combine into a resilient chain
    llm_chain = primary_model.with_fallbacks([secondary_model])

    def log_service(ai_message):
        metadata = ai_message.response_metadata
        model_name = metadata.get("model_name", "Unknown Cloud Model")
        print(f"--- [SERVICE LOG]: Served by {model_name} ---")
        return ai_message

    return llm_chain | RunnableLambda(log_service)