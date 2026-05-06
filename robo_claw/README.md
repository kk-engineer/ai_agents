# Robo Claw
An AI Agent that responds to queries on your WhatsApp(self) and CLI.

You can run the LLM locally or integrate via API.

# 1. Getting Started (local LLM) 🚀
1.1 Use llama.cpp (Preferred, as faster on Mac)
```bash
brew install cmake
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
cmake -B build -DGGML_METAL=ON
cmake --build build --config Release
```

1.2  Install Ollama
Before running the project, you must have Ollama installed to manage your local LLMs.

- [Download Ollama](https://ollama.com/download/).

# 2. Set Up the Model
2.1 For llama.cpp (mistral-nemo-12b)

*Note*: Run commands in llama.cpp directory
## Download the model
```bash
brew install aria2
aria2c -x 16 -s 16 "https://huggingface.co/bartowski/Mistral-Nemo-Instruct-2407-GGUF/resolve/main/Mistral-Nemo-Instruct-2407-Q4_K_M.gguf?download=true" -d models -o mistral-nemo-12b.gguf
```

## Run the model
*Note*: Run commands in llama.cpp directory
```bash
./build/bin/llama-server -m models/mistral-nemo-12b.gguf --n-gpu-layers -1 --ctx-size 8192 --port 8000
```
*Note*: Downloading the model from internet will take 5-10 mins(depending upon internet speed)

*Note*: You can also try Qwen model (they are faster), but call terminal(shell) tool for everything.
Will need to fix the prompt accordingly.

### Download and run Qwen 2.5 
*Note*: Run commands in llama.cpp directory
```bash
cd /models
curl -L https://huggingface.co/bartowski/Qwen2.5-Coder-7B-Instruct-GGUF/resolve/main/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf -o qwen2.5-7b.gguf
cd ..
./build/bin/llama-server \\n-m models/qwen2.5-7b.gguf \\n--n-gpu-layers -1 \\n--ctx-size 8192 \\n--port 8000
```
2.2 For Ollama (gemma4:e4b model)
Once Ollama is installed, pull and run the specific version of a model:

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
cd ai_agents/robo_claw

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

# 4. Run the App
``` bash
python3 app.py
```

