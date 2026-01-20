# Docker Setup Explained

## 📁 Files Overview

### Configuration Files

- **`Dockerfile`** - Defines how to build the Docker image (both dev and prod)
- **`docker-compose.base.yml`** - Base configuration shared by dev and prod
- **`docker-compose.dev.yml`** - Development-specific settings (Jupyter, hot reload, etc.)
- **`docker-compose.prod.yml`** - Production-specific settings (resource limits, security)
- **`dev.sh`** - Helper script to make Docker commands easier

### How They Work Together

```
docker-compose.base.yml     <- Shared config (Qdrant, base agent setup)
       +
docker-compose.dev.yml      <- Development overrides (Jupyter, mounted volumes)
       =
Full dev environment
```

## 🚀 Usage

### Development (Daily Work)

```bash
# Start everything (Qdrant + Agent + Jupyter)
./dev.sh up

# Or start in background
./dev.sh upd

# Open shell in container
./dev.sh shell

# Inside the shell, run scripts
python scripts/scrape_insurance_data.py

# View logs
./dev.sh logs

# Open Jupyter in browser
./dev.sh jupyter

# Stop everything
./dev.sh down
```

### Rebuilding (After Adding Dependencies)

```bash
# Rebuild from scratch (picks up new dependencies)
./dev.sh rebuild-deps

# Then start
./dev.sh up
```

### Local Development (Outside Docker)

```bash
# One-time setup
./scripts/setup_local.sh

# Then just run Jupyter locally
jupyter lab
```

## 🔧 What Happens When You Run `./dev.sh up`

1. Reads `docker-compose.base.yml` + `docker-compose.dev.yml`
2. Builds the Docker image using `Dockerfile` (development stage)
3. Installs all Python dependencies
4. Installs Playwright browsers (for web scraping)
5. Starts 3 containers:
   - **qdrant** - Vector database on port 6333
   - **agent** - Main application (your code)
   - **jupyter** - JupyterLab on port 8888
6. Mounts your local `src/`, `data/`, and `.env` into containers (hot reload)

## 🏭 Production

```bash
# Build and start production
docker-compose -f docker-compose.base.yml -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.base.yml -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.base.yml -f docker-compose.prod.yml logs -f

# Stop
docker-compose -f docker-compose.base.yml -f docker-compose.prod.yml down
```

**Production differences**:
- No Jupyter container
- No mounted source code (uses code from build time)
- Resource limits (CPU/memory)
- Qdrant not exposed externally
- Auto-restart enabled

## 🎯 Key Points

1. **Playwright is now installed automatically** in Docker ✅
2. **For local dev**, run `./scripts/setup_local.sh` once ✅
3. **Use `./dev.sh`** for all Docker operations - it's simpler ✅
4. **Development and production use the same Dockerfile** - just different stages ✅

## 🐛 Troubleshooting

### "Playwright not found" error in Docker
```bash
# Rebuild from scratch
./dev.sh rebuild-deps
```

### "Playwright not found" error locally
```bash
# Run setup script
./scripts/setup_local.sh
```

### Changes to `pyproject.toml` not picked up
```bash
# Rebuild without cache
./dev.sh rebuild-deps
```

### Port already in use
```bash
# Check what's running
./dev.sh status

# Stop everything
./dev.sh down
```

## 📚 Why This Setup?

- **Simple**: Just use `./dev.sh` commands
- **Consistent**: Dev and prod use same Dockerfile
- **Fast**: Code changes hot-reload in development
- **Complete**: Playwright installed automatically everywhere
- **Clean**: No duplicate config files
