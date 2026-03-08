# Results Table Specificatie

Gebaseerd op de live vergelijkingstool op vergelijk.expatverzekering.nl.

---

## Tabel Layout

Twee identieke tabellen: Ziektekostenverzekeringen en Reisverzekeringen.

### Tabel wrapper (MUI Paper)

```css
.table-wrapper {
  border-radius: 8px;
  border: 1px solid rgb(222, 226, 230);    /* #DEE2E6 */
  box-shadow: none;
  background: #FFF;
  overflow: auto;
}
```

### Tabel zelf

```css
table {
  width: 100%;
  border-collapse: collapse;
  border: none;
  background: transparent;
}
```

---

## Kolommen

| Kolom              | Breedte   | Inhoud                         | Text-align |
|--------------------|-----------|--------------------------------|------------|
| Verzekeraar/Dekking | ~49%      | Logo + naam (clickable)        | left       |
| Budget             | ~16%      | Prijs of status                | right      |
| Medium             | ~17%      | Prijs of status                | right      |
| Top                | ~18%      | Prijs of status                | right      |

### Header rij

```css
table thead th {
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 17.6px;          /* ~1.1rem */
  font-weight: 600;
  color: rgb(0, 114, 218);    /* #0072DA - blauw */
  background: transparent;
  padding: 16px;
  text-align: left;
  border-bottom: 1px solid rgb(224, 224, 224);  /* #E0E0E0 */
}
/* Prijs-kolommen rechts uitgelijnd */
table thead th:not(:first-child) {
  text-align: right;
}
```

### Data rijen

```css
table tbody tr {
  cursor: pointer;
  transition: background-color 0.15s ease;
  border-bottom: none;
}

/* Rij hover */
table tbody tr:hover {
  background-color: rgb(248, 249, 250);  /* #F8F9FA */
}

/* Goedkoopste/geselecteerde rij - groen highlight */
table tbody tr.cheapest {
  background-color: rgb(209, 242, 209);  /* #D1F2D1 */
}
```

### Verzekeraar cel (eerste kolom)

```css
td.cell-insurer {
  display: flex;              /* of via interne div */
  align-items: center;
  gap: 12px;
  padding: 16px;
  text-align: left;
  vertical-align: middle;
  border-bottom: 1px solid rgb(224, 224, 224);
}
```

#### Logo in rij

```css
.cell-insurer__logo {
  width: 60px;
  height: 60px;
  object-fit: contain;
  border-radius: 0;
  flex-shrink: 0;
}
```

#### Verzekeraar naam (clickable button)

```css
.cell-insurer__name {
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 17.6px;
  font-weight: 600;
  color: #000;
  background: transparent;
  border: none;
  padding: 0;
  cursor: pointer;
  text-align: left;
}
```

### Prijs cellen

```css
td.cell-price {
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 14px;
  font-weight: 500;
  color: #000;
  text-align: right;
  padding: 16px;
  vertical-align: middle;
  border-bottom: 1px solid rgb(224, 224, 224);
  white-space: nowrap;
}
```

---

## Weergave regels

| JSON waarde          | Weergave           | Stijl                               |
|----------------------|--------------------|--------------------------------------|
| Getal (bijv. 103)    | `€103`             | font-weight 500, color #000         |
| `"website"`          | `Website`          | font-weight 500, color #000         |
| `null` / unavailable | `Niet beschikbaar` | font-weight 500, color #000         |

**Let op:** De live site maakt geen kleuronderscheid voor "Niet beschikbaar" of "Website" - alle cellen zijn zwart 14px, weight 500.

---

## Sectie Header (boven tabel)

```css
.results-section__title {
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 24px;
  font-weight: 700;
  color: rgb(0, 114, 218);    /* #0072DA */
  line-height: 32px;
  margin: 0 0 24px;
}
```

### Subtitel (onder heading)

```css
.results-section__subtitle {
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 14px;
  font-weight: 400;
  color: rgb(102, 102, 102);  /* #666666 */
  margin: 0 0 24px;
}
```

Voorbeeld tekst: `Eigen risico: €500 • Totaalbedrag voor alle personen • Maandelijkse premies`

---

## Expandable Rows (Detail Panel)

Elke data-rij wordt gevolgd door een detail-rij (standaard verborgen).
Klik op rij -> detail panel verschijnt.

### HTML structuur

```html
<tr class="result-row">
  <td class="cell-insurer">
    <img class="cell-insurer__logo" src="..." alt="...">
    <button class="cell-insurer__name">Globality Yougenio</button>
  </td>
  <td class="cell-price">€103</td>
  <td class="cell-price">€177</td>
  <td class="cell-price">€310</td>
</tr>
<tr class="detail-row" style="display: none;">
  <td colspan="4">
    <div class="detail-panel">...</div>
  </td>
</tr>
```

### Detail panel styling

```css
.detail-row td {
  padding: 0;
  border-bottom: none;
}

.detail-panel {
  background: rgb(248, 249, 250);  /* #F8F9FA - lichtgrijs */
  padding: 24px;
  display: block;
}

.detail-panel__description {
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 17.6px;
  font-weight: 400;
  color: rgb(102, 102, 102);      /* #666666 */
  line-height: 28.16px;           /* 1.6 */
  margin-bottom: 16px;
}
```

### Detail panel links

```css
.detail-panel__links {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.detail-panel__link {
  display: block;
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 14px;
  font-weight: 500;
  color: rgb(0, 114, 218);        /* #0072DA */
  background: transparent;
  border: 1px solid rgb(0, 114, 218);
  border-radius: 4px;
  padding: 6px 12px;
  text-decoration: none;
  cursor: pointer;
}

.detail-panel__link:hover {
  background: rgb(0, 114, 218);
  color: #FFF;
}
```

Link types: `Website`, `Premie`, `Dekking`, `Aanvragen`

---

## Eigen Risico Dropdown (boven tabel)

```css
.eigen-risico__label {
  font-size: 14px;
  font-weight: 400;
  color: #000;
}

.eigen-risico__select {
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 16px;
  font-weight: 400;
  color: #000;
  border: 1px solid rgb(222, 226, 230);
  border-radius: 4px;
  padding: 16.5px 32px 16.5px 14px;
  height: auto;
  background: #FFF;
}
```

---

## Rij highlight logica

- **Standaard**: transparante achtergrond
- **Goedkoopste per kolom**: `background-color: rgb(209, 242, 209)` (lichtgroen)
- **Detail panel open**: detail-rij krijgt `background: rgb(248, 249, 250)`
- **Hover**: `background-color: rgb(248, 249, 250)` (lichtgrijs)

---

## Actie buttons onder tabellen

```css
.results-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

/* E-mail / Print buttons */
.results-actions__button {
  font-size: 14px;
  font-weight: 500;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

/* Vraag advies link */
.results-actions__advies {
  font-size: 14px;
  font-weight: 500;
  color: rgb(0, 114, 218);
  text-decoration: none;
}

/* Terug naar formulier */
.results-actions__back {
  font-size: 14px;
  cursor: pointer;
}
```

---

## Responsive

Op mobiel (< 768px):
- Tabel wrapper scrollt horizontaal (`overflow-x: auto`)
- Eerste kolom (verzekeraar) kan sticky zijn
- Detail panel stapt naar verticale layout

---

*Zie [design_tokens.md](design_tokens.md) voor het volledige kleurenpalet en spacing systeem.*
*Screenshot referentie: [reference_results_fullpage.png](reference_results_fullpage.png)*
