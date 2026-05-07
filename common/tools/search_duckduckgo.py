import streamlit as st
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper


def get_duckduckgo_search_tool():
    wrapper = DuckDuckGoSearchAPIWrapper(max_results=3)
    return DuckDuckGoSearchRun(api_wrapper=wrapper)