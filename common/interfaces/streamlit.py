import streamlit as st
import time

# Local imports
from common.core.agent_logic import call_agent, clear_chat_history


def run_streamlit():
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

    # --- AGENT EXECUTION ---
    if st.session_state.processing:
        # Get the actual last query from session state
        current_prompt = st.session_state.messages[-1]["content"]

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # 1. Start the timer
                    start_time = time.time()
                    output = call_agent(current_prompt)
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

