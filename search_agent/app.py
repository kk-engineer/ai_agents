import streamlit as st
from langchain_classic.agents import AgentExecutor, create_react_agent

# Local imports
from llm_config.local_llm import get_ollama_llm
from llm_config.online_llm import get_cloud_llm
from llm_config.prompt import prompt
from tools.search_duckduckgo import get_duckduckgo_search_tool
from tools.search_tavily import get_tavily_tool
from tools.terminal_tool import get_terminal_tool

# -------------------------------
# 1. LLM Config
# -------------------------------
# Toggle this based on your current workspace/battery/internet
USE_LOCAL = True

if USE_LOCAL:
    llm = get_ollama_llm()
else:
    llm = get_cloud_llm()

# -------------------------------
# 2. Tools
# -------------------------------
USE_DUCKDUCKGO = True

if USE_DUCKDUCKGO:
    search = get_duckduckgo_search_tool()
else:
    search = get_tavily_tool()

terminal = get_terminal_tool()
tools = [search, terminal]

# -------------------------------
# 3. Agent & Executor
# -------------------------------
agent = create_react_agent(llm, tools, prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,  # This catches the error and asks the LLM to fix it
    max_iterations=3
)

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
                # Format simple history string for the prompt
                history_str = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-5:-1]])

                # Assume agent_executor is defined in your backend setup
                response = agent_executor.invoke({
                   "input": current_prompt,
                   "chat_history": history_str
                })
                output = response["output"]

                # Simulation for demonstration
                #output = f"Processed: {current_prompt}"

            except Exception as e:
                output = f"I encountered an error: {str(e)}"

            st.markdown(output)
            st.session_state.messages.append({"role": "assistant", "content": output})

    # Unlock the input
    st.session_state.processing = False
    st.rerun()