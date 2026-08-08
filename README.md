# AI Command Line Agent (CrewAI Terminal Assistant)

An intelligent, AI-powered Command Line Interface (CLI) assistant built using **CrewAI** and **Python**. It translates natural language prompts into automated local actions using a two-agent sequential architecture (Router & Executor) and executes them using specialized tools.

## Architecture Flow

The system uses a sequential agent pipeline:
1.  **Router Agent**: Analyzes your natural language command, determines the intent category (Shell, File, Code, Git), and builds a structured step-by-step execution plan.
2.  **Executor Agent**: Equipped with custom Python toolsets, it carries out the Router's plan by executing local terminal or file operations.
3.  **Output Layer**: Receives the raw result and formats it into a premium, colored terminal UI using the `rich` library.

---

## Prerequisites
* Python 3.10 to 3.13
* Git

---

## Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/Ayushsingh-02082004/ai-terminal-assistant.git
cd ai-terminal-assistant
```

### 2. Set up a Virtual Environment
It is recommended to run the project in a clean virtual environment:
```bash
python -m venv venv

# Activate it (Windows PowerShell):
.\venv\Scripts\Activate.ps1

# Activate it (macOS/Linux):
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 4. Configure your Environment variables
Create your local `.env` file in the `backend/` folder:
```bash
cp backend/.env.example backend/.env
```
Open `backend/.env` and fill in your **Ollama Cloud** (or custom endpoint) credentials:
```ini
OLLAMA_API_KEY=your_private_api_key_here
OLLAMA_MODEL_NAME=gemma4:31b-cloud
OLLAMA_API_BASE=https://ollama.com/v1
```

---

## Running the CLI Agent
To start the interactive loop, navigate to the `backend/` directory and run:
```bash
cd backend
python run.py
```

### Example Commands to Try:
*   `list all files in the current folder`
*   `create a file named hello.txt with the content "Hello World"`
*   `check the git status of the repository`
*   `verify the python syntax of backend/run.py`
*   `find the file names in the backend folder whose size is less than 20 MB`

---

## Project Structure
*   `backend/run.py` — Application launcher.
*   `backend/src/cli_agent/main.py` — CLI user loop.
*   `backend/src/cli_agent/crew.py` — Orchestrator tying LLMs, agents, and tasks together.
*   `backend/src/cli_agent/config/agents.yaml` — Declarative roles for Router and Executor.
*   `backend/src/cli_agent/config/tasks.yaml` — Declarative routing and execution tasks.
*   `backend/src/cli_agent/services/` — Custom Python tools (Shell, File, Code, Git).
*   `backend/src/cli_agent/utils/formatter.py` — CLI terminal output styling.
