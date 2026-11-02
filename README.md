# Agent Workbench

A small Python project demonstrating an AI agent that can choose and call real tools.

The idea is straightforward: instead of only returning generated text, the model can request a tool, provide its arguments, receive the tool result and use that result to answer the user.

This is a learning/demo project, not a production agent framework.

## What it can do

| Tool | Purpose | Service |
|---|---|---|
| `calculate` | Safely evaluates basic arithmetic | Local Python |
| `get_current_time` | Returns the current UTC time | Local Python |
| `get_weather` | Looks up current conditions for a city | Open-Meteo |
| `get_github_repository` | Reads public repository details | GitHub REST API |

The model cannot run arbitrary Python or shell commands. It can only call functions registered in `agent_workbench/tools.py`.

## How the agent works

1. The CLI receives a user prompt.
2. The Python client sends the prompt and tool declarations to Gemini.
3. Gemini either returns a normal answer or requests a function call.
4. The application checks the requested function against its tool registry.
5. The function runs and returns data or a controlled error.
6. The tool result is sent back to Gemini.
7. Gemini writes a response using the returned information.

The loop has a configurable maximum number of steps.

## Project layout

```text
agent-workbench/
├── agent_workbench/
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── gemini.py
│   └── tools.py
├── tests/
│   └── test_tools.py
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

## Requirements

- Python 3.10+
- Gemini API key
- Internet access for Gemini, Open-Meteo and GitHub requests

Create an API key in [Google AI Studio](https://aistudio.google.com/).

## Run locally

### 1. Clone your repository

```bash
git clone https://github.com/YOUR_USERNAME/agent-workbench.git
cd agent-workbench
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install the project

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

### 4. Configure the API key

Copy `.env.example` to `.env`.

PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS / Linux:

```bash
cp .env.example .env
```

Edit `.env`:

```env
GEMINI_API_KEY=your_real_key_here
GEMINI_MODEL=gemini-2.5-flash
AGENT_MAX_STEPS=6
HTTP_TIMEOUT=20
```

Keep `.env` private. Never commit your API key.

### 5. Start the agent

```bash
agent-workbench
```

Or:

```bash
python -m agent_workbench.cli
```

## Example prompts

```text
What is 18 percent of 2450?
```

```text
What's the current weather in Owerri?
```

```text
Check the public GitHub repository microsoft/vscode and summarize its stars, language and description.
```

```text
What time is it in UTC?
```

The weather and GitHub tools make external HTTP requests. Calculation and time run locally.

## Tests

```bash
pytest
```

The tests cover arithmetic, operator precedence, unsafe expression rejection and unknown tool handling. They do not require an API key and do not call external services.

## Adding a tool

1. Write a Python function in `agent_workbench/tools.py`.
2. Add a matching function declaration to `TOOL_DEFINITIONS`.
3. Register the function in `FUNCTIONS`.
4. Add tests for normal and invalid inputs.

The declaration describes the tool to Gemini. The registry controls which Python functions the application is actually allowed to run.

## Safety and limitations

- No arbitrary shell or Python execution is exposed to the model.
- The calculator uses Python's AST parser and an operator allowlist; it does not use `eval()`.
- External requests use timeouts.
- GitHub access is limited to public repository metadata.
- Weather availability depends on Open-Meteo.
- Each prompt is currently a fresh request; there is no persistent conversation memory.
- There is no web interface, user account system, background worker or production monitoring.
- Gemini usage may be subject to provider quotas and charges. Check current terms and pricing before running repeated requests.

## Troubleshooting

**Missing API key:** confirm `.env` is in the project root and contains a valid key.

**Gemini API error:** check the key, model availability and network connection. Change `GEMINI_MODEL` in `.env` if needed.

**Weather lookup fails:** try a different spelling or a larger nearby city.

**GitHub repository not found:** check the owner and repository spelling. Private repositories are not supported.

## Why this project exists

I wanted a compact project to understand the practical connection between an LLM and software that can take actions. It brings together function calling, tool registration, API requests, result handling, basic safety controls and tests in one codebase.

## License

MIT. See [LICENSE](LICENSE).
