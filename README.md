# ResilienceBot Lab4

This repository contains a simple **retrieval‑augmented generation (RAG)**
bot designed for reliability engineering troubleshooting checklists.  The
core components are:

1. **CLI entrypoint** (`app/main.py`) – accepts a question, runs the bot, and
   prints a checklist plus diagnostics.
2. **ResilienceBot wrapper** (`app/core/bot.py`) – builds prompts, calls an LLM
   client, and post‑processes output.
3. **Local LLM client** (`app/clients/hf_local.py`) – interfaces with a
   HuggingFace FLAN‑T5 model running in a local virtualenv.
4. **Retrieval layer** (`app/rag/*`) – embeds a small knowledge base and
   returns relevant context chunks.
5. **Safe wrapper** (`app/llm/safe_wrapper.py`) – shields the CLI from
   generation errors and optionally retries.

A stub `hf_pipeline_local.py` is provided for compatibility with older code that
previously used a differently‑named client.

## Installation

```powershell
# create and activate a venv on Windows
python -m venv .venv
& .venv\Scripts\Activate.ps1

# install dependencies
c:/ResilienceBot_Lab4/.venv/Scripts/python.exe -m pip install -r requirements.txt
```

> ⚠️ Make sure the virtual environment is active whenever you run any of the
> scripts; otherwise you may see `ModuleNotFoundError` for packages such as
> `sentence_transformers` or `torch`.

## Usage

### CLI

```powershell
python -m app.main "My API has intermittent 504 timeouts. Give a troubleshooting checklist."
```

The output will include a numbered checklist, retrieval diagnostics and
model latency statistics.  Internally, the CLI uses `safe_generate` to guard
against runtime failures.
#### Example response

A typical run produces something like:

```
ResilienceBot (RAG):

- Check the upstream service latency dashboards
- Check the connection pool usage metrics
- Check the database latency metrics
- Look for recent deployments or config changes
- Inspect application logs for timeout errors

---
Success: True
Used fallback: False
Attempts: 1
Latency: 12345 ms
```

(The exact checklist items vary with the question and context.)
### Running the RAG pipeline test

A lightweight script demonstrates retrieval and full bot behavior:

```powershell
python -m app.test_rag_pipeline
```

You can adapt or extend this file to add additional manual test cases.  For
example, change the `question` variable near the top to try different prompts.

## Writing new test cases

The repository does not currently include a formal test suite, but you can
add unit tests under a `tests/` directory using `pytest`.  Focus on

* `app/core/bot.py` – verify prompt construction and post‑processing.
* `app/clients/hf_local.py` – test normalization and retry logic using mocked
  LLM responses.
* `app/rag/retriever.py` – ensure retrieval returns expected chunks for
  sample queries.

When adding tests, invoke them with:

```powershell
# assuming pytest is installed in the venv
python -m pytest tests
```

## Project structure

```
app/
  clients/          # LLM client implementations
  core/             # bot logic & schemas
  llm/              # auxiliary helpers (safe_wrapper)
  rag/              # retrieval/embedding code
  utils/            # shared utilities (logger, etc.)
  main.py           # CLI entrypoint
  test_rag_pipeline.py  # manual pipeline verification script

data/              # sample documents and precomputed index
logs/               # runtime logs
requirements.txt    # Python dependencies
README.md           # this file
```

## Contributing

1. Fork the repository and create a feature branch.
2. Add or update tests for any changed behavior.
3. Run the CLI and pipeline test to ensure nothing breaks.
4. Open a pull request with a description of your changes.

Feel free to update the README with additional examples or instructions
before pushing to GitHub.

## 📄 Concept Overview

For a **visual explanation of the architecture and design decisions**, see the conceptual showcase:

➡️ **Concept Page (Gist)**
https://gist.github.com/anonymousgirl123/5e87f5623d4481993239f317d8c2a067

---

# 🚀 Project Goal

Production incidents often require **fast and structured troubleshooting**. Engineers must quickly identify potential failure points across infrastructure, services, and deployments.

ResilienceBot assists **Site Reliability Engineers (SREs)** by automatically generating **clear investigation checklists** using a local language model.

This project demonstrates how **LLMs can be integrated into operational tooling** to support incident investigation workflows.

---

# 🧠 Key Engineering Concepts

This project demonstrates several important AI engineering patterns:

* **Local LLM inference** using HuggingFace Transformers
* **Prompt engineering** to enforce structured outputs
* **Deterministic model generation** for consistent results
* **Output normalization** using regex post-processing
* **Modular architecture** separating prompt logic from model clients
* **CLI-based interaction** for operational environments

---

# 🏗 Architecture

The system follows a modular architecture:

```
User CLI
   ↓
ResilienceBot Wrapper
   ↓
HFLocalClient
   ↓
FLAN-T5 Local Model
   ↓
Checklist Output
```

### Component Overview

**CLI Interface**

* Accepts user troubleshooting questions
* Invokes the ResilienceBot wrapper

**ResilienceBot Wrapper**

* Builds structured prompts
* Injects system instructions
* Passes requests to the LLM client

**HFLocalClient**

* Loads HuggingFace model locally
* Handles tokenization and generation
* Performs response normalization

**FLAN-T5 Model**

* Generates structured troubleshooting steps
* Runs locally using PyTorch

---

# ⚙️ System Flow

1. User submits a troubleshooting question through the CLI.
2. ResilienceBot constructs a structured prompt with system instructions.
3. The request is passed to the HFLocalClient.
4. The HuggingFace
