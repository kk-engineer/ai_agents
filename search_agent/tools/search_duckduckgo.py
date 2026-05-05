import streamlit as st
from langchain_community.tools import DuckDuckGoSearchRun

@st.cache_data(ttl=300)
def get_duckduckgo_search_tool():
    return DuckDuckGoSearchRun()