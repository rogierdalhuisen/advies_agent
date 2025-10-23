# Claude Code Setup for Advies Agent

## Quick Start

This directory contains configuration for effective agentic coding with Claude Code.

## Available Slash Commands

Use these commands by typing `/command-name` in Claude Code:

- `/plan` - Create a structured implementation plan for a new feature
- `/dev-start` - Start the Docker development environment
- `/dev-stop` - Stop the Docker development environment
- `/test-qdrant` - Test Qdrant connection and list collections
- `/lint` - Run ruff linting on the codebase
- `/review` - Review changes against coding standards

## Referencing Project Files

Use `@` to reference important files in your prompts:

- `@.claude/CONTRIBUTING.md` - Coding standards and workflow
- `@.claude/IMPLEMENTATION_PLAN.md` - Template for feature planning

## Recommended Workflows

### Starting a New Feature

1. Use `/plan Feature description here` to create an implementation plan
2. Review and discuss the plan
3. Approve and let Claude implement following the plan
4. Use `/review` before committing

### Daily Development

1. Use `/dev-start` to spin up your environment
2. Work on features with context from `@.claude/CONTRIBUTING.md`
3. Use `/lint` to check code quality
4. Use `/test-qdrant` to verify vector store integration
5. Use `/review` before creating PRs

### Docker Commands

Your project uses:
- `docker-compose.dev.yml` - Development with hot-reload
- Main services: agent, qdrant, jupyter
- Python managed with `uv`

## Tips for Effective Agentic Coding

1. **Be Specific** - Reference exact files or features you want to change
2. **Use Templates** - For big features, always start with `/plan`
3. **Iterate** - Review plans before implementation, provide feedback
4. **Context** - Use `@` to include relevant files in your prompts
5. **Standards** - Claude automatically follows CONTRIBUTING.md, but you can reference it explicitly

## Project Structure

```
advies_agent/
├── src/                 # Python source code
├── data/                # Data files and documents
├── .claude/             # Claude Code configuration
│   ├── commands/        # Slash commands
│   ├── CONTRIBUTING.md  # Coding standards
│   └── IMPLEMENTATION_PLAN.md  # Feature plan template
├── docker-compose.*.yml # Docker configurations
└── pyproject.toml       # Python dependencies (managed by uv)
```

## Environment Setup

This project uses:
- **Python 3.12+** with `uv` package manager
- **LangChain + LangGraph** for AI agents
- **Qdrant** for vector storage
- **Docker Compose** for orchestration

Remember to activate your environment: `source .venv/bin/activate`
