import streamlit as st
import time
from langchain_classic.agents import AgentExecutor, create_react_agent

# Local imports
from llm_config.local_llm import get_ollama_llm
from llm_config.online_llm import get_cloud_llm
from llm_config.prompt import prompt
from tools.search_duckduckgo import get_duckduckgo_search_tool
from tools.search_tavily import get_tavily_tool
from tools.terminal_tool import get_terminal_tool

USE_LOCAL_LLM = True
USE_DUCKDUCKGO = True
llm = None

@st.cache_resource
def initialize_app():
    # -------------------------------
    # 1. LLM Config
    # -------------------------------
    # Toggle this based on your current workspace/battery/internet
    llm = get_ollama_llm() if USE_LOCAL_LLM else get_cloud_llm()

    # -------------------------------
    # 2. Tools
    # -------------------------------
    web_search = get_duckduckgo_search_tool() if USE_DUCKDUCKGO else get_tavily_tool()
    terminal = get_terminal_tool()

    tools = [web_search, terminal]

    # -------------------------------
    # 3. Agent & Executor
    # -------------------------------
    agent = create_react_agent(llm, tools, prompt)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,  # This catches the error and asks the LLM to fix it
        max_iterations=2
    )

    return agent_executor, llm

agent_executor, llm = initialize_app()

# -------------------------------
# 4. UI & Config
# -------------------------------
st.set_page_config(page_title="RoboSathi AI Agent", page_icon="🪼")
st.title("🪼 RoboSathi AI Agent")

# ---  CUSTOM UI STYLING ---
st.markdown("""
    <style>
        /* Change Chat Icons to Meta Blue */
        [data-testid="stChatMessageAvatarUser"] { background-color: #0866FF !important; }
        [data-testid="stChatMessageAvatarAssistant"] { background-color: #0866FF !important; }
        [data-testid="stChatMessageAvatarUser"] svg, 
        [data-testid="stChatMessageAvatarAssistant"] svg { fill: white !important; }

        /* Force SF Pro / System Font */
        html, body, [class*="css"] {
            font-family: "-apple-system", "BlinkMacSystemFont", "SF Pro Display", sans-serif !important;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# 5. UI Loop
# -------------------------------

def is_simple_greeting(text):
    greetings = ["hi", "hello", "hey", "who are you", "thanks", "bye", "what's up"]
    return text.lower().strip() in greetings

# ---  SESSION STATE MANAGEMENT ---
if "processing" not in st.session_state:
    st.session_state.processing = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "user":
            st.markdown(msg["content"])
        else:
            st.markdown(msg["content"])


if user_query := st.chat_input("Ask your query...", disabled=st.session_state.processing):
    st.session_state.processing = True
    # Save to history immediately
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.rerun()

# --- 5. AGENT EXECUTION ---
if st.session_state.processing:
    # Get the actual last query from session state
    current_prompt = st.session_state.messages[-1]["content"]

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # 1. Start the timer
                start_time = time.time()
                # Format simple history string for the prompt
                history_str = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-2:]])

                if is_simple_greeting(current_prompt):
                    # Call the LLM directly without the ReAct overhead
                    response_text = llm.invoke(f"The user said '{current_prompt}'. Give a short, friendly greeting.")
                    output = response_text.content
                else:
                    # Use the full Agent for complex tasks
                    response = agent_executor.invoke({"input": current_prompt, "chat_history": history_str})
                    output = response["output"]
                # 2. Calculate elapsed time
                end_time = time.time()
                elapsed_time = round(end_time - start_time, 2)

                # 3. Append the time to the output string
                output_with_time = f"{output}\n\n---\n*⏱️ Response time: {elapsed_time} seconds*"

            except Exception as e:
                output_with_time = f"I encountered an error: {str(e)}"

            st.markdown(output_with_time)
            # Save the version with the timestamp to session state
            st.session_state.messages.append({"role": "assistant", "content": output_with_time})

        # Unlock the input
        st.session_state.processing = False
        st.rerun()
