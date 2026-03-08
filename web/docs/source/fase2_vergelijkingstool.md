# Fase 2: Vergelijkingstool

## Formulierpagina (`/tool`)

### Invoervelden

| Veld                | Type                    | Opties                                              | Bron      |
| ------------------- | ----------------------- | --------------------------------------------------- | --------- |
| Geboortedatum       | Date picker             | —                                                   | Vrij      |
| Nationaliteit       | Radio/select            | Nederland, België, Anders                           | config.py |
| Bestemmingsland     | Text/select             | Vrij invullen of dropdown                           | —         |
| Vertrekdatum        | Date picker             | —                                                   | Vrij      |
| Duur van reis       | Select                  | 0-6 mnd, 6-12 mnd, 1-2 jr, 2-5 jr, >5 jr, permanent | config.py |
| Hoofdreden verblijf | Multi-select checkboxes | Reizen, Werken, Pensioen, Anders                    | config.py |
| Partner             | Toggle ja/nee           | Bij ja: geboortedatum                               | —         |
| Kinderen            | Teller (0-n)            | Per kind: geboortedatum                             | —         |

### Technisch

- Alpine.js: partner toggle (toont/verbergt geboortedatum), kinderen teller (voeg veld toe/verwijder)
- HTMX: `hx-post="/api/compare"` op submit
- Na submit: redirect naar `/tool/resultaten?session_id=xxx`

---

## API: POST /api/compare

### Request

```json
{
  "age": 35,
  "destination": "Spain",
  "departure_date": "2026-03-15",
  "nationality": "Nederland",
  "duration": "1-2 jaar",
  "main_reasons": ["werken", "reizen"],
  "has_partner": true,
  "age_partner": 33,
  "children": true,
  "child_ages": [8, 6]
}
```

**Nieuwe velden t.o.v. oude structuur:**

- `nationality` (was er niet) — filtert welke verzekeraars getoond worden
- `duration` (was er niet) — filtert welke verzekeraars getoond worden
- `main_reasons` (was er niet) — filtert welke verzekeraars getoond worden

### Response

```json
{
  "session_id": "abc123",
  "input_summary": {
    "age": 35,
    "destination": "Spain",
    "has_partner": true,
    "children_count": 2,
    "duration": "1-2 jaar"
  },
  "Internationale Ziektekostenverzekeringen": {
    "Allianz Global": {
      "Budget": {
        "premies": { "0": 89, "250": 78, "500": 67, "1000": 56, "2500": 45 },
        "coverage": {
          "inpatient": true,
          "outpatient": true,
          "dental": false,
          "maternity": false
        }
      },
      "Medium": {
        "premies": { "0": 125, "250": 112, "500": 98, "1000": 85, "2500": 72 },
        "coverage": {
          "inpatient": true,
          "outpatient": true,
          "dental": true,
          "maternity": false
        }
      },
      "Top": {
        "premies": {
          "0": 156,
          "250": 142,
          "500": 128,
          "1000": 114,
          "2500": 100
        },
        "coverage": {
          "inpatient": true,
          "outpatient": true,
          "dental": true,
          "maternity": true
        }
      }
    },
    "Goudse Expat Pakket": {
      "Budget": {
        "premies": {
          "0": 76,
          "250": 68,
          "500": 59,
          "1000": 51,
          "2500": "website"
        },
        "coverage": {
          "inpatient": true,
          "outpatient": true,
          "dental": false,
          "maternity": false
        }
      },
      "Medium": {
        "premies": { "0": 98, "250": 87, "500": 76, "1000": 65, "2500": null },
        "coverage": {
          "inpatient": true,
          "outpatient": true,
          "dental": true,
          "maternity": false
        }
      }
    }
  },
  "Internationale Reisverzekeringen": {
    "Allianz Global": {
      "Budget": {
        "premies": { "0": 34, "250": 31, "500": 28, "1000": 25, "2500": 22 },
        "coverage": {
          "inpatient": false,
          "outpatient": true,
          "dental": false,
          "maternity": false
        }
      },
      "Medium": {
        "premies": { "0": 52, "250": 47, "500": 42, "1000": 37, "2500": 32 },
        "coverage": {
          "inpatient": true,
          "outpatient": true,
          "dental": false,
          "maternity": false
        }
      },
      "Top": {
        "premies": { "0": 71, "250": 64, "500": 57, "1000": 50, "2500": 43 },
        "coverage": {
          "inpatient": true,
          "outpatient": true,
          "dental": true,
          "maternity": false
        }
      }
    }
  }
}
```

**Filtering:** Verzekeringen die niet beschikbaar zijn voor de opgegeven duur,
nationaliteit of hoofdreden verschijnen niet in de response. Dit wordt
afgehandeld door het backend filter in `src/vergelijker/`.

**Nieuw t.o.v. oude response:**

- `session_id` — koppelt resultaten aan chatsessie
- `input_summary` — samenvatting voor weergave op resultatenpagina
- `coverage` object per dekkingsniveau — voor de negatief-filter checkboxes

### Waarden in de response

| JSON waarde                               | Weergave in tabel             |
| ----------------------------------------- | ----------------------------- |
| Getal (bijv. `89`)                        | €89/mnd                       |
| `"website"`                               | "Zie website"                 |
| `null` , `nvt`, or anything that is empty | ✗ (kruisje, niet beschikbaar) |

---

### Backend premielogica

De premieberekening bestaat uit twee stappen in `src/vergelijker/`:

**1. Filter (nieuw te bouwen):**

- Input: duur, nationaliteit, hoofdreden verblijf
- Databron: Excel bestand (nog te maken) met per verzekering welke
  duur/nationaliteit/reden geldig zijn
- Output: lijst van verzekeringen die in aanmerking komen

**2. Calculator (bestaand, aan te passen):**

- Input: age, destination, departure_date, has_partner, age_partner,
  children, child_ages
- Output: premies per verzekering per dekkingsniveau per eigen risico
- Bestaande code in `src/vergelijker/`, moet aangepast worden om de
  nieuwe response structuur (coverage per niveau) te leveren

Beide stappen vallen buiten scope van de web-implementatie.
De web-laag gaat ervan uit dat de JSON response structuur zoals
hierboven beschreven wordt aangeleverd door `compare_service.py`.

## Resultatenpagina (`/tool/resultaten`)

### Layout

```
┌─────────────────────────────────────────────────┐
│ Samenvatting: "35 jaar, Spanje, met partner..."  │
├─────────────────────────────────────────────────┤
│ FILTERS:                                         │
│ Eigen risico: [dropdown 0/250/500/1000/2500]     │
│ ☐ Inpatient  ☐ Outpatient  ☐ Dental  ☐ Maternity│
├─────────────────────────────────────────────────┤
│                                                   │
│ INTERNATIONALE ZIEKTEKOSTENVERZEKERINGEN          │
│ ┌──────────────┬──────────┬──────────┬──────────┐│
│ │ Verzekeraar  │ Budget   │ Medium   │ Top      ││
│ ├──────────────┼──────────┼──────────┼──────────┤│
│ │ Allianz      │ €89/mnd  │ €125/mnd │ €156/mnd ││
│ │  ↳ [detail]  │          │          │          ││
│ │ Goudse       │ €76/mnd  │ €98/mnd  │ ✗        ││
│ │ Cigna        │ ✗        │ €134/mnd │ €198/mnd ││
│ └──────────────┴──────────┴──────────┴──────────┘│
│                                                   │
│ INTERNATIONALE REISVERZEKERINGEN                  │
│ ┌──────────────┬──────────┬──────────┬──────────┐│
│ │ Verzekeraar  │ Budget   │ Medium   │ Top      ││
│ │ ...          │          │          │          ││
│ └──────────────┴──────────┴──────────┴──────────┘│
│                                                   │
│ (sectie verdwijnt als geen verzekeraars van       │
│  dat type beschikbaar zijn)                       │
│                                                   │
├─────────────────────────────────────────────────┤
│ CHAT SECTIE (stub, later implementeren)           │
├─────────────────────────────────────────────────┤
│ EXTRA TOOLS (toekomstig, leeg blok)               │
└─────────────────────────────────────────────────┘
```

### Filters gedrag

**Eigen risico dropdown:**

- Wijzigt de premies in de tabel
- HTMX: `hx-get="/api/compare/table?session_id=xxx&deductible=500"`
- Server retourneert partial HTML (alleen de tabellen)
- HTMX swapt het tabel-gedeelte

**Coverage checkboxes (negatief filter):**

- Standaard: alle premies zichtbaar
- Bij aanvinken: kruisjes verschijnen bij dekkingsniveaus die dat coverage type NIET bieden
- Voorbeeld: vink "Dental" aan → Goudse Budget krijgt ✗ want `dental: false`
- Dit kan client-side met Alpine.js (data is al in de pagina) OF server-side met HTMX
- Aanbeveling: client-side met Alpine.js (sneller, geen extra request)

### Uitklapbare rij

- Klik op verzekeraar-rij → HTMX `hx-get="/api/compare/detail/{verzekeraar_id}"`
- Retourneert `partials/results_row_detail.html`
- Wordt onder de rij ingevoegd
- Inhoud is configureerbaar (nog te bepalen wat er precies in staat)

### Dataflow

```
1. Formulier submit
   → POST /api/compare (JSON body)
   → compare_service.py → bestaande src/ premielogica
   → Response JSON met session_id
   → Redirect naar /tool/resultaten?session_id=xxx

2. Resultatenpagina laadt
   → GET /tool/resultaten?session_id=xxx
   → Server haalt resultaten op (in-memory of cache)
   → Jinja2 rendert volledige pagina

3. Eigen risico wijzigen
   → HTMX GET /api/compare/table?session_id=xxx&deductible=500
   → Server retourneert partial HTML (beide tabellen)
   → HTMX swapt tabel-sectie

4. Coverage filter
   → Alpine.js client-side: toggle kruisjes op basis van coverage data
   → Geen server request nodig

5. Rij uitklappen
   → HTMX GET /api/compare/detail/{id}?session_id=xxx
   → Server retourneert detail partial
   → HTMX voegt in onder de rij
```

---

### Session opslag

In-memory dict in `compare_service.py`:

```python
compare_sessions: dict[str, dict] = {}
```

Resultaten worden opgeslagen na POST /api/compare en opgehaald bij
GET /tool/resultaten. Geen Redis/database nodig voor MVP.

Let op: bij server restart gaan sessies verloren. Acceptabel voor MVP.

### Uitklapbare rij inhoud

Per verzekering toont de detail-rij:

- Korte beschrijving (tekst)
- Logo verzekeraar
- Vier links: Website, Premie, Dekking, Aanvragen (allemaal naar expatverzekering.nl)

Patroon is voor elke verzekering hetzelfde.

**Databron:** `web/static/data/insurance_details.json`
Logo's in `web/static/img/logos/`
Geladen via `config.py` met `json.load()`.

Structuur per verzekering in JSON:

```json
{
  "OOM Wonen in het buitenland": {
    "description": "Internationaal verzekeringspakket voor...",
    "logo": "oom-logo.svg",
    "links": {
      "website": "https://www.expatverzekering.nl/...",
      "premie": "https://www.expatverzekering.nl/...#chapter-493",
      "dekking": "https://www.expatverzekering.nl/.../dekkingsoverzicht.pdf",
      "aanvragen": "https://www.expatverzekering.nl/...#chapter-494"
    }
  }
}
```

Het JSON-bestand moet nog gevuld worden met alle 16 verzekeringen.

### Sorteer-logica

**Standaard volgorde:** Handmatige lijst in config. Makkelijk aanpasbaar
door namen om te wisselen.

Voorlopige volgorde:

1. goudse_expat_pakket
2. oom_wib
3. oom_tib
4. cigna_global_care
5. cigna_close_care
6. allianz_care
7. allianz_globetrotter
8. globality_yougenio
9. expatriate_group
10. ACS
11. IMG\_
12. MSH
13. special_isis
14. goudse_ngo_zendelingen
15. goudse_working_nomad
16. International Expat Insurance

**Sorteer op prijs:**

- Één knop boven beide tabellen
- Gebruiker kiest kolom: Budget, Medium of Top
- Sorteert altijd goedkoopst bovenaan bij het geselecteerde eigen risico
- Verzekeringen zonder premie in die kolom komen onderaan
- Knop "Standaard volgorde" zet de handmatige lijst terug

## Stappen

- [ ] web/services/compare_service.py — koppeling met bestaande premielogica
- [ ] POST /api/compare — accepteert formulierdata, retourneert JSON + session_id
- [ ] GET /api/compare/table — retourneert partial HTML tabel (voor HTMX)
- [ ] GET /api/compare/detail/{id} — retourneert detail partial
- [ ] resultaten.html — twee tabelsecties + filters
- [ ] partials/results_table.html — tabel partial
- [ ] partials/results_row_detail.html — uitklapbare rij
- [ ] HTMX: formulier submit → redirect
- [ ] Alpine.js: eigen risico dropdown
- [ ] Alpine.js: coverage checkboxes → kruisjes
- [ ] Testen: volledige flow

---
