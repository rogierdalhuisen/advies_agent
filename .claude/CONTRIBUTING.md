# Code Quality Guidelines

1. Write idiomatic code, don't take shortcuts
2. For bigger requests, analyze and make a plan, and ask for approval before starting a large implementation
3. Keep comments focused on explaining the 'why' underneath implementation decisions. NEVER write non-value-adding comments that are a verbatim description of self-explanatory code, for example things like Parse(input) // parse input is not allowed.

# Activating environment

This repo uses uv as the python package manager.

the whole package is run using docker-compose, see dev.sh in root folder for instructions to run the application

## Installing packages

When installing packages, use the uv add $package command. Make sure that you have first activated your environment.

For example, to install pandas, run:

source .venv/bin/activate && uv add pandas

## Dependency Management

- Do NOT create requirements.txt. Use pyproject.toml + uv.lock.
- Manage all deps in the root pyproject.toml.
- After adding deps: activate venv and run uv sync.
- Use uv run to execute Python scripts with the correct environment.

## Environment Variables

- Store all env vars in the root .env (backend, dashboard, CLI share it).
- Load with python-dotenv (use load_dotenv() — it finds the root .env).

# Boy scout rules

After bigger implementations, analyze what small improvements could be taken along in the same PR and propose to make the required changes for these improvements.
