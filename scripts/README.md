# Scripts Directory

This directory contains utility scripts for the insurance advice agent project.

## Available Scripts

### `setup_local.sh`

**Purpose**: Set up your local development environment (outside Docker)

**When to use**: Run this once when you first clone the repo or when dependencies change

**What it does**:
- Installs Python dependencies using `uv`
- Installs Playwright browsers for web scraping

**Usage**:
```bash
./scripts/setup_local.sh
```

### `ingest_documents.py`

**Purpose**: Ingest insurance documents into Qdrant vector database

**Usage**:
```bash
# Ingest all documents
python scripts/ingest_documents.py

# Recreate collection (delete existing data)
python scripts/ingest_documents.py --recreate

# Use specific embedding provider
python scripts/ingest_documents.py --use-openai
python scripts/ingest_documents.py --use-gemini
```

### `scrape_insurance_data.py`

**Purpose**: Scrape insurance provider websites and save as markdown

**Usage**:
```bash
# List all configured providers
python scripts/scrape_insurance_data.py --list-providers

# Scrape all providers
python scripts/scrape_insurance_data.py

# Scrape specific provider
python scripts/scrape_insurance_data.py --provider goudse_expat_pakket

# Dry run (don't save files)
python scripts/scrape_insurance_data.py --dry-run
```

### `monthly_update.sh`

**Purpose**: Monthly automated update - scrape websites and re-ingest documents

**Usage**:
```bash
./scripts/monthly_update.sh
```

**Automation**: Set up as a cron job to run monthly:
```bash
# Add to crontab (runs on 1st of each month at 2 AM)
0 2 1 * * cd /path/to/advies_agent && ./scripts/monthly_update.sh
```

## Development Workflow

### Local Development (Jupyter notebooks)

1. **First time setup**:
   ```bash
   ./scripts/setup_local.sh
   ```

2. **Run Jupyter**:
   ```bash
   jupyter lab
   ```

### Docker Development

1. **Start environment**:
   ```bash
   ./dev.sh up
   ```

2. **Run scripts in Docker**:
   ```bash
   ./dev.sh shell
   python scripts/scrape_insurance_data.py
   ```

### Production

Use the monthly update script or run individual scripts as needed:
```bash
./scripts/monthly_update.sh
```
