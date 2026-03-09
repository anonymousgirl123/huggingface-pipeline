# 🤖 ResilienceBot – Local LLM SRE Troubleshooting Assistant

A lightweight **command-line AI assistant** that generates structured troubleshooting checklists for production incidents using a **local HuggingFace LLM (FLAN-T5)**.

---

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
