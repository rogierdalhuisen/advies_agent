# Masterplan: AI Tool Integratie expatverzekering.nl

## Status: COMPLEET — klaar om te bouwen

### Detaildocumenten

| Document | Inhoud |
|----------|--------|
| [fase1_backend_fundament.md](fase1_backend_fundament.md) | FastAPI setup, mappenstructuur, dependencies, commands |
| [fase2_vergelijkingstool.md](fase2_vergelijkingstool.md) | Formulier, tabel, filters, API request/response, dataflow |
| [fase3_chat_stubs.md](fase3_chat_stubs.md) | Chat UI, endpoints, suggestie-chips, markdown rendering |
| [visuele_integratie.md](visuele_integratie.md) | Exacte header/footer HTML, CSS strategie, fonts, kleuren |
| [config_referentie.md](config_referentie.md) | Alle configureerbare waarden op één plek |
| [claude_code_instructies.md](claude_code_instructies.md) | CLAUDE.md inhoud + takenlijst per fase |

---

## 1. Projectoverzicht

**Doel:** Eigen webapplicatie via reverse proxy op `expatverzekering.nl/tool`, met:

1. **Vergelijkingstool** — Premieoverzicht op basis van klantgegevens
2. **AI Chat** (later) — Vraagbalk onderaan resultatenpagina
3. **Toekomstige uitbreidingen** — Modulaire architectuur

**Codebase:** Zelfde repo als `advies_agent`, zelfde `uv` virtual env, zelfde `src/` modules.

---

## 2. Architectuur

```
[Browser] → https://expatverzekering.nl/tool/*
    → [Extern bedrijf webserver — reverse proxy]
    → [Jouw VPS — FastAPI + Jinja2 + HTMX + Alpine.js]
    → [Bestaande src/ modules voor premieberekening + RAG]
```

**Stack:** FastAPI, Jinja2, HTMX 2.x, Alpine.js 3.x, uv, Docker Compose
**Geen:** React, npm, Node.js, build-stap

---

## 3. Pagina-structuur

```
/tool                → Formulierpagina
/tool/resultaten     → Resultaten (2 tabellen) + Chat (vast blok onderaan)
```

Resultatenpagina is modulair opgebouwd uit blokken:
- Ziektekostenverzekeringen tabel
- Reisverzekeringen tabel
- Chat sectie
- Extra tools sectie (toekomstig)

---

## 4. Projectstructuur

```
advies_agent/
├── src/                             ← bestaand (NIET wijzigen)
├── web/                             ← NIEUW
│   ├── app.py                       ← FastAPI entrypoint
│   ├── config.py                    ← alle configureerbare waarden
│   ├── routes/
│   │   ├── pages.py                 ← GET /tool, GET /tool/resultaten
│   │   ├── compare.py               ← POST /api/compare
│   │   ├── chat.py                  ← POST /api/chat (stub)
│   │   └── health.py
│   ├── services/
│   │   ├── compare_service.py       ← roept src/ premielogica aan
│   │   └── chat_service.py          ← stub
│   ├── templates/
│   │   ├── base.html                ← header + footer layout
│   │   ├── tool.html                ← formulier
│   │   ├── resultaten.html          ← modulaire resultatenpagina
│   │   └── partials/
│   │       ├── results_table.html
│   │       ├── results_row_detail.html
│   │       ├── chat_section.html
│   │       └── chat_message.html
│   └── static/
│       ├── css/main.css             ← theme + header/footer
│       ├── css/components.css       ← eigen componenten
│       ├── js/htmx.min.js
│       ├── js/alpine.min.js
│       └── js/app.js
├── data/
├── docker-compose.prod.yml
├── CLAUDE.md
└── pyproject.toml
```

---

## 5. Stappenplan

### Fase 0: Voorbereiding ✅
- [x] WhatsApp naar extern bedrijf
- [x] Alle technische beslissingen genomen
- [ ] CLAUDE.md in project root
- [ ] `uv add fastapi jinja2 uvicorn python-multipart sse-starlette`

### Fase 1: Backend fundament → [details](fase1_backend_fundament.md)
### Fase 2: Vergelijkingstool → [details](fase2_vergelijkingstool.md)
### Fase 3: Chat stubs → [details](fase3_chat_stubs.md)
### Fase 4: Polish
### Fase 5: Deployment

---

## 6. Beslissingen

| Beslissing | Status |
|-----------|--------|
| Frontend: HTMX + Alpine.js + Jinja2 | ✅ |
| Twee routes: /tool + /tool/resultaten | ✅ |
| Twee tabellen: ziektekostenverzekering + reisverzekering | ✅ |
| Chat: vast blok onderaan, suggestie-chips, markdown | ✅ |
| CSS 1-op-1 overnemen (3-lagen) | ✅ |
| Premies per maand, totaalprijs gezin | ✅ |
| Eigen risico: 0, 250, 500, 1000, 2500 | ✅ |
| Coverage checkboxes als negatief filter | ✅ |
| Uitklapbare rijen voor detail | ✅ |
| Config-bestand voor alle aanpasbare waarden | ✅ |
| Modulaire blokken voor uitbreidbaarheid | ✅ |
| Chat: alleen stubs nu, implementatie later | ✅ |
| Twee processen: web + chainlit (intern) | ✅ |
| Hosting: Hetzner of DigitalOcean | ⏳ |
| URL pad: /tool (afstemmen extern bedrijf) | ⏳ |
| Coverage data per verzekeraar | ⏳ nog bouwen/aanvullen |

---

*Laatst bijgewerkt: 7 maart 2026*
