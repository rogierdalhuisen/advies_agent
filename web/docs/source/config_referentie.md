# Config Referentie

Alle configureerbare waarden staan in `web/config.py`.
Wijzigingen hier = geen templates aanpassen.

---

## Formulier opties

```python
NATIONALITEIT_OPTIES = ["Nederland", "België", "Anders"]

DUUR_OPTIES = [
    "0-6 maanden",
    "6-12 maanden",
    "1-2 jaar",
    "2-5 jaar",
    "langer dan 5 jaar",
    "permanent",
]

HOOFDREDEN_OPTIES = [
    {"key": "reizen", "label": "Reizen"},
    {"key": "werken", "label": "Werken"},
    {"key": "pensioen", "label": "Pensioen"},
    {"key": "anders", "label": "Anders"},
]
```

---

## Resultaten filters

```python
EIGEN_RISICO_OPTIES = [0, 250, 500, 1000, 2500]

COVERAGE_FILTERS = [
    {"key": "inpatient", "label": "Inpatient (ziekenhuisopname)"},
    {"key": "outpatient", "label": "Outpatient (ambulante kosten)"},
    {"key": "dental", "label": "Dental (Tandheelkunde)"},
    {"key": "maternity", "label": "Maternity (Zwangerschap en bevalling)"},
]
```

---

## Tabel

```python
DEKKINGSNIVEAUS = ["Budget", "Medium", "Top"]
MAX_VERZEKERAARS = 16
PREMIE_WEERGAVE = "maand"  # premies per maand

VERZEKERING_TYPES = [
    "Internationale Ziektekostenverzekeringen",
    "Internationale Reisverzekeringen",
]
```

---

## Tabel weergave regels

```python
# Hoe speciale waarden getoond worden in de tabel
WEERGAVE_REGELS = {
    "website": "Zie website",      # str "website" in JSON
    None: "✗",                      # null in JSON
    "not_available": "✗",           # ontbrekend dekkingsniveau
}

PREMIE_FORMAT = "€{prijs}/mnd"     # bijv. €89/mnd
```

---

## Chat

```python
CHAT_SUGGESTIE_CHIPS = [
    "Wat dekt een Budget pakket?",
    "Welke verzekering past het beste bij mij?",
    "Waarom verschilt de prijs per verzekeraar?",
    "Wat is het verschil tussen inpatient en outpatient?",
]

CHAT_ENABLED = False  # zet op True als chat geïmplementeerd is
CHAT_MAX_HISTORY = 20  # max berichten in history
```

---

## TODO: Waarden nog te bepalen

- [ ] Eigen risico opties definitief bevestigen
- [ ] Suggestie-chips teksten finaliseren
- [ ] Uitklapbare rij: welke detail-velden tonen
