# Task Breakdown Agent

An AI-powered REST API that turns a high-level goal into a concrete, ordered set of actionable steps. Given a domain of expertise (`field`) and an objective (`task`), the service uses a locally-hosted LLM (via [Ollama](https://ollama.com)) orchestrated through [LangGraph](https://langchain-ai.github.io/langgraph/) to return a structured, machine-readable list of instructions.

The value proposition is simple: get reliable, schema-validated step-by-step plans from a private, self-hosted model — no third-party API keys, no data leaving your machine, and guaranteed JSON output thanks to structured generation.

## Features

- **REST API powered by FastAPI** — exposes a single `POST /run-agent` endpoint with automatic request/response validation and interactive docs at `/docs`.
- **Local, private inference via Ollama** — runs any Ollama-compatible model (configurable through an environment variable), keeping prompts and data on your own infrastructure.
- **LangGraph workflow orchestration** — task processing is modeled as a compiled state graph (`START → give_steps → END`), making the pipeline easy to extend with additional nodes.
- **Structured, schema-validated output** — uses `with_structured_output` and Pydantic models to guarantee the LLM returns a clean `List[str]` of steps rather than free-form text.
- **Domain-aware prompting** — the agent is dynamically instructed to act as an expert in the requested `field` before generating its plan.
- **Environment-based configuration** — the target model is supplied via a `.env` file, so swapping models requires no code changes.

## Prerequisites

Before running the project, make sure you have the following installed and available:

- **Python 3.9+**
- **pip** (or another Python package manager such as `uv` or `poetry`)
- **[Ollama](https://ollama.com/download)** installed and running locally
- **A pulled Ollama model** capable of structured/tool output (e.g. `llama3.1`, `qwen2.5`, `mistral`)

You can verify Ollama is running and pull a model with:

```bash
ollama pull llama3.1
ollama list
```

## Getting Started

Follow these steps to get a local instance running.

### 1. Clone the repository

```bash
git clone https://github.com/Chavaphon/BreakDown
cd BreakDown
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate      # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install fastapi uvicorn langchain-ollama langchain-core langgraph pydantic python-dotenv
```

> Tip: save these to a `requirements.txt` file and run `pip install -r requirements.txt` for reproducible installs.

### 4. Configure environment variables

Create a `.env` file in the project root and set the Ollama model the agent should use. The model name must match one you have pulled via `ollama pull`.

```bash
# .env
MODEL=llama3.1
```

### 5. Run the server

```bash
python main.py
```

The API will start on `http://0.0.0.0:8000`. Interactive Swagger documentation is available at `http://localhost:8000/docs`.

> Alternatively, run it with the Uvicorn CLI and live-reload during development:
> ```bash
> uvicorn main:app --reload --host 0.0.0.0 --port 8000
> ```

## API Usage Example

### Endpoint

`POST /run-agent`

**Request body**

| Field   | Type     | Description                  |
| ------- | -------- | ---------------------------- |
| `field` | `string` | The field/domain of interest |
| `task`  | `string` | The task to accomplish       |

**Response body**

| Field   | Type            | Description                          |
| ------- | --------------- | ------------------------------------ |
| `steps` | `array[string]` | Ordered list of steps to accomplish the task |

### Example with `curl`

```bash
curl -X POST "http://localhost:8000/run-agent" \
  -H "Content-Type: application/json" \
  -d '{
        "field": "Home Gardening",
        "task": "start a small balcony herb garden"
      }'
```

**Example response**

```json
{
  "steps": [
    "Choose a sunny spot on your balcony that gets at least 6 hours of light.",
    "Select beginner-friendly herbs such as basil, mint, and parsley.",
    "Pick containers with drainage holes and fill them with potting mix.",
    "Plant seeds or seedlings at the recommended depth and spacing.",
    "Water regularly and harvest leaves once the plants are established."
  ]
}
```

### Example with Python (`requests`)

```python
import requests

response = requests.post(
    "http://localhost:8000/run-agent",
    json={
        "field": "Software Development",
        "task": "set up a CI/CD pipeline for a Python project",
    },
)

data = response.json()
for i, step in enumerate(data["steps"], start=1):
    print(f"{i}. {step}")
```

### Example with JavaScript (`fetch`)

```javascript
const response = await fetch("http://localhost:8000/run-agent", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    field: "Personal Finance",
    task: "build an emergency fund",
  }),
});

const data = await response.json();
console.log(data.steps);
```