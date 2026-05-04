# Search Agent
A simple implementation of Web search + Terminal commands calling agent using local LLM (also online LLM). 

This project focuses on building autonomous systems capable of doing web search when the LLM does not have required information 
to answer the question or run commands on your Mac terminal to give you information about the system, such as, available free space.

# 1. Getting Started 🚀
1. Install Ollama
Before running the project, you must have Ollama installed to manage your local LLMs.

- [Download Ollama](https://ollama.com/download/).

# 2. Set Up the Model
This project is optimized for the Gemma4:e4b model. 
Once Ollama is installed, pull and run the specific version:

```bash
# Pull the model (this may take some time, depends on your internet speed)
ollama pull gemma4:e4b
```
*Note*: I am running the model on M1 Mac 16 GB RAM.

In case your system has lower RAM then - you can use smaller model, such as, "qwen2.5-coder:7b-instruct".

# 3. Clone and Setup Project
```bash
# Clone the repository
git clone https://github.com/kk-engineer/ai_agents.git
cd ai_agents/search_agent

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

# 4. Run Streamlit App
``` bash
streamlit run app.py
```

