# Claude Code Instructies

## CLAUDE.md (kopieer naar project root)

```markdown
# Project: expatverzekering.nl AI Tool

## Wat
Webapplicatie voor expatverzekering.nl — vergelijkingstool + AI chat.
Draait achter reverse proxy op /tool/*.

## Stack
- Backend: FastAPI (Python 3.12) met Jinja2 templates
- Frontend: HTMX + Alpine.js (geen React, geen npm, geen build stap)
- AI: LangGraph orchestrator + RAG (bestaand in src/)
- DB: PostgreSQL
- Package manager: uv
- Deployment: Docker Compose

## Structuur
- src/ → bestaande AI/data modules (NIET wijzigen zonder overleg)
- web/ → webapplicatie
- web/config.py → alle configureerbare waarden (formulier opties, filters, etc.)
- web/routes/ → FastAPI route handlers
- web/services/ → business logic (roept src/ aan)
- web/templates/ → Jinja2 HTML templates
- web/templates/partials/ → HTMX partial templates
- web/static/ → CSS, JS, afbeeldingen
- data/ → verzekerings data en documenten

## Regels
- Alle pagina routes beginnen met /tool/
- Alle API routes beginnen met /api/
- Gebruik bestaande modules uit src/ — dupliceer GEEN logica
- Nieuwe business logic in web/services/, NIET in routes
- Configureerbare waarden in web/config.py, NIET hardcoded in templates
- Python: type hints, async waar mogelijk
- HTML: Jinja2 templates, HTMX voor dynamische delen
- Interactiviteit: Alpine.js (x-data, x-model, x-show)
- GEEN npm, GEEN Node.js, GEEN build stap
- Test elke endpoint met curl voor je verder gaat
- Commit na elke werkende feature

## Commands
- Dev server: uv run uvicorn web.app:app --reload --port 8000
- Test: uv run pytest
- Docker: docker-compose -f docker-compose.prod.yml up

## API response formaat
- /api/compare retourneert JSON met session_id + verzekeraars per type
- Twee types: "Internationale Ziektekostenverzekeringen" en "Internationale Reisverzekeringen"
- Per verzekeraar: premies per dekkingsniveau (Budget/Medium/Top) per eigen risico
- Speciale waarden: null = niet beschikbaar, "website" = zie website
- Per verzekeraar: coverage object (inpatient/outpatient/dental/maternity booleans)
- /api/compare/table retourneert partial HTML voor HTMX swap
- /api/compare/detail/{id} retourneert detail partial HTML
- /api/chat retourneert SSE stream (stub, nog niet geïmplementeerd)
```

---

## Werkwijze

### Gouden regels

1. **Plan Mode eerst** — Shift+Tab+Tab. Lees code, maak plan, PAS DAN bouwen.
2. **Kleine taken** — 5-15 minuten per taak. Eén ding tegelijk.
3. **Commit vaak** — Na elke werkende feature.
4. **Verificeer** — Test na elke stap voordat je doorgaat.

### Voorbeeldprompts per fase

Geef deze prompts één voor één aan Claude Code. Wacht op voltooiing en test voordat je de volgende geeft.

---

## Fase 1 taken

```
Taak 1.1:
Maak de volledige mappenstructuur voor web/ aan:
- web/__init__.py
- web/app.py (leeg)
- web/config.py (leeg)
- web/routes/__init__.py
- web/routes/pages.py (leeg)
- web/routes/compare.py (leeg)
- web/routes/chat.py (leeg)
- web/routes/health.py (leeg)
- web/services/__init__.py
- web/services/compare_service.py (leeg)
- web/services/chat_service.py (leeg)
- web/templates/ (leeg)
- web/templates/partials/ (leeg)
- web/static/css/ (leeg)
- web/static/js/ (leeg)
- web/static/img/ (leeg)
```

```
Taak 1.2:
Maak web/app.py aan met:
- FastAPI app
- Jinja2Templates(directory="web/templates")
- StaticFiles mount op /static
- Include routers uit web/routes/
- Proxy headers middleware (TrustedHostMiddleware)
- Config importeren en beschikbaar maken voor templates
```

```
Taak 1.3:
Maak web/routes/health.py met GET /health die {"status": "ok"} retourneert.
Test met: curl localhost:8000/api/health
```

```
Taak 1.4:
Maak web/config.py aan met alle configureerbare waarden.
Zie docs/config_referentie.md voor de complete lijst.
```

```
Taak 1.5:
Maak web/templates/base.html aan met:
- HTML boilerplate (charset, viewport, title block)
- Links naar /static/css/main.css en /static/css/components.css
- HTMX en Alpine.js script tags (defer)
- Header HTML van expatverzekering.nl (zie docs/visuele_integratie.md)
- Content block
- Footer HTML van expatverzekering.nl
- Alle links absoluut (https://www.expatverzekering.nl/...)
```

```
Taak 1.6:
Maak web/templates/tool.html aan (extends base.html) met een statisch
formulier met alle invoervelden uit config.py. Nog zonder HTMX/Alpine.js.
Maak web/routes/pages.py met GET /tool die deze template rendert.
Test: open localhost:8000/tool in browser.
```

```
Taak 1.7:
Haal de CSS van expatverzekering.nl op en maak web/static/css/main.css
met: fonts, kleurenpalet, typografie, button styles, header/footer styles.
Maak web/static/css/components.css (leeg, voor later).
Test: localhost:8000/tool ziet er uit met correcte fonts en kleuren.
```

---

## Fase 2 taken

```
Taak 2.1:
Maak web/services/compare_service.py aan die de bestaande premieberekening
in src/ aanroept. Lees eerst src/agents/comparer/ en src/preprocessing/ om
te begrijpen hoe de huidige logica werkt. Maak een functie die de nieuwe
request structuur accepteert en de juiste response retourneert.
```

```
Taak 2.2:
Maak POST /api/compare in web/routes/compare.py.
Accepteert de formulierdata, roept compare_service aan, retourneert JSON.
Test met curl.
```

```
Taak 2.3:
Maak web/templates/resultaten.html (extends base.html) met:
- Input samenvatting bovenaan
- Filters sectie (eigen risico dropdown + coverage checkboxes)
- Tabel sectie (wordt gevuld door partial)
- Chat sectie (placeholder)
- Extra tools sectie (leeg)
Maak GET /tool/resultaten in pages.py.
```

```
Taak 2.4:
Maak web/templates/partials/results_table.html met de vergelijkingstabel.
Twee secties: Ziektekostenverzekeringen en Reisverzekeringen.
Rijen = verzekeraars, kolommen = Budget/Medium/Top.
Toon €prijs/mnd, "Zie website", of ✗.
Sectie verdwijnt als geen verzekeraars van dat type.
```

```
Taak 2.5:
Voeg HTMX toe aan tool.html: formulier submit POST naar /api/compare,
bij succes redirect naar /tool/resultaten?session_id=xxx.
```

```
Taak 2.6:
Voeg Alpine.js toe aan resultaten.html:
- Eigen risico dropdown: hx-get naar /api/compare/table met HTMX swap
- Coverage checkboxes: client-side kruisjes toggle op basis van coverage data
```

```
Taak 2.7:
Maak web/templates/partials/results_row_detail.html en
GET /api/compare/detail/{id} endpoint.
Voeg HTMX toe: klik op rij → laad detail partial.
```

```
Taak 2.8:
Test de volledige flow:
1. Open /tool
2. Vul formulier in
3. Submit → redirect naar resultaten
4. Wijzig eigen risico → tabel update
5. Vink coverage aan → kruisjes verschijnen
6. Klik op rij → detail klapt uit
```

---

## Fase 3 taken

```
Taak 3.1:
Maak web/services/chat_service.py als stub.
Definieer de interface: send_message(message, history, session_id) en
set_context(session_id, compare_results). Implementatie retourneert placeholder.
```

```
Taak 3.2:
Maak POST /api/chat en POST /api/chat/context als stub endpoints.
```

```
Taak 3.3:
Maak web/templates/partials/chat_section.html met:
- Suggestie-chips uit config.py
- Berichten container (leeg)
- Invoerveld + verstuurknop (disabled)
- "Chat wordt binnenkort beschikbaar" melding
Voeg het blok toe in resultaten.html.
```

---

## Tips

- Als Claude Code afdwaalt: druk Escape, gebruik /rewind
- Als context vol raakt: gebruik /compact
- Refereer altijd naar specifieke bestanden met @ (tab-completion)
- Geef Claude URLs naar HTMX docs als het vastloopt: https://htmx.org/docs/
- Alpine.js docs: https://alpinejs.dev/start-here
