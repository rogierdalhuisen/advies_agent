# Fase 1: Backend Fundament

## Dependencies

```bash
uv add fastapi jinja2 uvicorn python-multipart sse-starlette
```

## Stappen

### 1.1 Mappenstructuur aanmaken

Maak de volledige `web/` structuur aan met lege `__init__.py` bestanden.
Zie projectstructuur in [MASTERPLAN.md](MASTERPLAN.md).

### 1.2 FastAPI app (web/app.py)

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI()

# Templates en static files
templates = Jinja2Templates(directory="web/templates")
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# Routers
from web.routes import pages, compare, chat, health
app.include_router(health.router, prefix="/api")
app.include_router(compare.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(pages.router)
```

**Let op:**

- Proxy headers middleware toevoegen (X-Forwarded-For, X-Forwarded-Proto)
- Config importeren voor template context
- Templates object beschikbaar maken voor routes

### 1.3 Health endpoint

```python
# web/routes/health.py
from fastapi import APIRouter
router = APIRouter()

@router.get("/health")
async def health():
    return {"status": "ok"}
```

Test: `curl localhost:8000/api/health`

### 1.4 Base template (base.html)

Kopieer de volledige header uit visuele_integratie.md Stap 2 en de footer uit Stap 3 in base.html.
Structuur:

### 1.5 CSS ophalen (3-lagen aanpak)

Zie [visuele_integratie.md](visuele_integratie.md) voor de volledige aanpak.

**Volgorde:**

1. Meet header/footer CSS via Chrome DevTools MCP (zie Stap 5b in visuele_integratie.md)
2. Schrijf `main.css` op basis van gemeten waarden + fonts (Stap 4) + kleuren (Stap 5)
3. Kopieer `components.css` uit Stap 6

### 1.6 Formulierpagina (statisch eerst)

Eerste versie van `tool.html` met de volgende velden
(zie fase2_vergelijkingstool.md voor alle details):

- Geboortedatum (date picker)
- Nationaliteit (radio: Nederland, België, Anders)
- Bestemmingsland (text/select)
- Vertrekdatum (date picker)
- Duur van reis (select: 0-6 mnd t/m permanent)
- Hoofdreden verblijf (multi-select checkboxes)
- Partner toggle (ja/nee, bij ja: geboortedatum)
- Kinderen teller (0-n, per kind: geboortedatum)
- Submit button

Eerste versie: puur HTML, nog zonder HTMX of Alpine.js interactie.
Doel: pagina laadt correct met expatverzekering.nl styling.

### 1.7 Testen

- [ ] `curl localhost:8000/api/health` → `{"status": "ok"}`
- [ ] `localhost:8000/tool` → formulierpagina met correcte header/footer
- [ ] CSS klopt: fonts, kleuren, header/footer zien er uit als expatverzekering.nl

## Commands

```bash
# Start dev server
uv run uvicorn web.app:app --reload --port 8000

# Test health
curl localhost:8000/api/health
```

---

## TODO: Exacte details nog toe te voegen

- [x] Exacte proxy headers configuratie → niet nodig voor dev,
      alleen bij deployment achter reverse proxy
- [x] HTMX en Alpine.js versie-nummers en download links: - HTMX 2.0.4: https://unpkg.com/htmx.org@2.0.4/dist/htmx.min.js - Alpine.js 3.14.9: https://cdn.jsdelivr.net/npm/alpinejs@3.14.9/dist/cdn.min.js - Download beide naar web/static/js/
