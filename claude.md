---
## 🧠 Project Overview

You’re building an **agentic system in Python** using **LangChain** and **LangGraph**.
The system is designed to flexibly integrate and test multiple components — including **RAG**, **tool use**, and other reasoning modules.
---

## 🧩 Development Guidelines

- Write **modular and practical code** — each component (e.g., RAG, retriever, memory, tool) should be independently testable and reusable.
- Keep **interfaces clean and minimal** so components can plug into a broader system.
- Focus on **production-like**, realistic code (avoid toy examples).
- Components should integrate smoothly within a **LangGraph graph** or **LangChain agent**.

---

## 🐳 Environment & Execution

The entire system runs via **Docker Compose**.
Use the helper script `dev.sh` in the project root for managing the environment.

### Commands

```bash
./dev.sh up        # Start environment
./dev.sh shell     # Open shell in agent container
./dev.sh logs      # View logs
```

### Running Containers

- **advies_agent_app** → main agent container
- **advies_agent_jupyter** → Jupyter dev environment
- **advies_agent_qdrant** → Qdrant vector database (for embeddings)

---

## 💾 Vector Store

A **Qdrant** instance is running in Docker and serves as the **vector store** for your project.
All vector embeddings and document chunks are stored and retrieved from this service.

Access from code:

```python
from langchain_qdrant import Qdrant
store = Qdrant(
    url="http://qdrant:6333",
)
```

---

## 🧩 Tech Stack

- **Python 3.10+**
- **LangChain** — for LLM tooling, chains, and agent logic
- **LangGraph** — for graph-based orchestration
- **Qdrant** — vector store backend
- **Docker & Docker Compose**

---

## ✅ Coding Principles

- Keep code **clear, concise, and modular**
- Use **dependency injection** where possible (easy component swapping)
- Write **self-contained examples** that can run inside Docker
- Keep **LLM provider configurable**
- Add **short, meaningful docstrings**

---

Would you like me to adapt this to the **Claude Code format** (with sections like `# Context`, `# Guidelines`, `# Tools`, so it’s read automatically by the agent)?
