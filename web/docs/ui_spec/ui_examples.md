# UI Examples

Voorbeelden van HTML structuur + CSS classes zodat toekomstige agents
direct UI code kunnen genereren.

---

## Formulier (tool.html)

```html
<div class="card" style="max-width: 720px; margin: 0 auto;">
  <h2 class="form-section__title">Uw gegevens</h2>

  <div class="formfield">
    <label class="formfield__label formfield__label--required">Geboortedatum</label>
    <input type="date" class="formfield__input" name="geboortedatum" required>
  </div>

  <div class="formfield">
    <label class="formfield__label formfield__label--required">Nationaliteit</label>
    <div class="formfield__radio-group">
      <label class="formfield__radio-label">
        <input type="radio" name="nationaliteit" value="Nederland" checked> Nederland
      </label>
      <label class="formfield__radio-label">
        <input type="radio" name="nationaliteit" value="België"> België
      </label>
      <label class="formfield__radio-label">
        <input type="radio" name="nationaliteit" value="Anders"> Anders
      </label>
    </div>
  </div>

  <div class="formfield">
    <label class="formfield__label formfield__label--required">Bestemmingsland</label>
    <input type="text" class="formfield__input" name="bestemmingsland"
           placeholder="Bijv. Spanje" required>
  </div>

  <div class="formfield">
    <label class="formfield__label formfield__label--required">Vertrekdatum</label>
    <input type="date" class="formfield__input" name="vertrekdatum" required>
  </div>

  <div class="formfield">
    <label class="formfield__label formfield__label--required">Duur van verblijf</label>
    <select class="formfield__select" name="duur" required>
      <option value="">Selecteer...</option>
      <option value="0-6 maanden">0-6 maanden</option>
      <option value="6-12 maanden">6-12 maanden</option>
      <option value="1-2 jaar">1-2 jaar</option>
      <option value="2-5 jaar">2-5 jaar</option>
      <option value="langer dan 5 jaar">Langer dan 5 jaar</option>
      <option value="permanent">Permanent</option>
    </select>
  </div>

  <div class="formfield">
    <label class="formfield__label">Hoofdreden verblijf</label>
    <div class="formfield__checkbox-group">
      <label class="formfield__checkbox-label">
        <input type="checkbox" name="hoofdreden" value="reizen"> Reizen
      </label>
      <label class="formfield__checkbox-label">
        <input type="checkbox" name="hoofdreden" value="werken"> Werken
      </label>
      <label class="formfield__checkbox-label">
        <input type="checkbox" name="hoofdreden" value="pensioen"> Pensioen
      </label>
      <label class="formfield__checkbox-label">
        <input type="checkbox" name="hoofdreden" value="anders"> Anders
      </label>
    </div>
  </div>

  <h2 class="form-section__title">Gezinssamenstelling</h2>

  <div class="formfield">
    <div class="toggle" x-data="{ partner: false }" @click="partner = !partner">
      <div class="toggle__switch" :class="partner && 'toggle--active'"></div>
      <span class="toggle__label">Ik heb een partner</span>
    </div>
  </div>

  <div class="formfield" x-show="partner">
    <label class="formfield__label">Geboortedatum partner</label>
    <input type="date" class="formfield__input" name="geboortedatum_partner">
  </div>

  <div class="formfield">
    <label class="formfield__label">Aantal kinderen</label>
    <div class="counter" x-data="{ count: 0 }">
      <button type="button" class="counter__btn" @click="count = Math.max(0, count - 1)">-</button>
      <span class="counter__value" x-text="count"></span>
      <button type="button" class="counter__btn" @click="count++">+</button>
      <input type="hidden" name="kinderen" :value="count">
    </div>
  </div>

  <button type="submit" class="form__submit">
    Vergelijk verzekeringen
  </button>
</div>
```

---

## Results Table

```html
<section class="results-section">
  <h2 class="results-section__title">Internationale Ziektekostenverzekeringen</h2>

  <div class="table-container">
    <table>
      <thead>
        <tr>
          <th>Verzekeraar</th>
          <th>Budget</th>
          <th>Medium</th>
          <th>Top</th>
        </tr>
      </thead>
      <tbody>
        <!-- Normale rij -->
        <tr class="result-row">
          <td>
            <div class="cell-insurer">
              <img class="cell-insurer__logo" src="/static/img/logos/allianz.svg" alt="">
              <span>Allianz Care</span>
              <span class="cell-insurer__toggle">&#9660;</span>
            </div>
          </td>
          <td class="cell-price cell-price--available">€89/mnd</td>
          <td class="cell-price cell-price--available">€125/mnd</td>
          <td class="cell-price cell-price--available">€156/mnd</td>
        </tr>
        <!-- Detail rij (hidden by default) -->
        <tr class="detail-row" style="display: none;">
          <td colspan="4">
            <div class="detail-panel">
              <img class="detail-panel__logo" src="/static/img/logos/allianz.svg" alt="Allianz Care">
              <div class="detail-panel__content">
                <p class="detail-panel__description">
                  Allianz Care biedt wereldwijde dekking met een uitgebreid
                  netwerk van ziekenhuizen en klinieken.
                </p>
                <div class="detail-panel__links">
                  <a class="detail-panel__link" href="#">Website</a>
                  <a class="detail-panel__link" href="#">Premie</a>
                  <a class="detail-panel__link" href="#">Dekking</a>
                  <a class="detail-panel__cta" href="#">Aanvragen</a>
                </div>
              </div>
            </div>
          </td>
        </tr>

        <!-- Rij met "Zie website" -->
        <tr class="result-row">
          <td>
            <div class="cell-insurer">
              <img class="cell-insurer__logo" src="/static/img/logos/goudse.svg" alt="">
              <span>Goudse Expat</span>
              <span class="cell-insurer__toggle">&#9660;</span>
            </div>
          </td>
          <td class="cell-price cell-price--available">€76/mnd</td>
          <td class="cell-price cell-price--available">€98/mnd</td>
          <td class="cell-price cell-price--unavailable">&#10007;</td>
        </tr>
        <tr class="detail-row" style="display: none;">
          <td colspan="4"></td>
        </tr>

        <!-- Rij met niet beschikbaar -->
        <tr class="result-row">
          <td>
            <div class="cell-insurer">
              <img class="cell-insurer__logo" src="/static/img/logos/cigna.svg" alt="">
              <span>Cigna Global</span>
              <span class="cell-insurer__toggle">&#9660;</span>
            </div>
          </td>
          <td class="cell-price cell-price--unavailable">&#10007;</td>
          <td class="cell-price cell-price--available">€134/mnd</td>
          <td class="cell-price cell-price--website">Zie website</td>
        </tr>
        <tr class="detail-row" style="display: none;">
          <td colspan="4"></td>
        </tr>
      </tbody>
    </table>
  </div>
</section>
```

---

## Filter Bar

```html
<div class="filters" x-data="{ deductible: '0', coverage: [] }">
  <!-- Eigen risico -->
  <div class="filters__group">
    <label class="filters__label">Eigen risico</label>
    <select class="formfield__select" x-model="deductible"
            hx-get="/api/compare/table"
            hx-target="#results-tables"
            hx-include="[name='session_id']"
            hx-vals='js:{deductible: this.value}'>
      <option value="0">€0</option>
      <option value="250">€250</option>
      <option value="500">€500</option>
      <option value="1000">€1.000</option>
      <option value="2500">€2.500</option>
    </select>
  </div>

  <!-- Coverage filters -->
  <div class="filters__group">
    <label class="filters__label">Dekking vereist</label>
    <div class="filters__chips">
      <label class="filter-chip" :class="coverage.includes('inpatient') && 'active'">
        <input type="checkbox" value="inpatient" x-model="coverage" hidden>
        Inpatient
      </label>
      <label class="filter-chip" :class="coverage.includes('outpatient') && 'active'">
        <input type="checkbox" value="outpatient" x-model="coverage" hidden>
        Outpatient
      </label>
      <label class="filter-chip" :class="coverage.includes('dental') && 'active'">
        <input type="checkbox" value="dental" x-model="coverage" hidden>
        Dental
      </label>
      <label class="filter-chip" :class="coverage.includes('maternity') && 'active'">
        <input type="checkbox" value="maternity" x-model="coverage" hidden>
        Maternity
      </label>
    </div>
  </div>
</div>
```

---

## Expandable Row (met HTMX)

```html
<!-- Klikbare rij -->
<tr class="result-row"
    hx-get="/api/compare/detail/allianz_care?session_id=abc123"
    hx-target="next tr > td"
    hx-swap="innerHTML"
    @click="$el.classList.toggle('expanded'); $el.nextElementSibling.style.display = $el.nextElementSibling.style.display === 'none' ? '' : 'none'">
  <td>
    <div class="cell-insurer">
      <span>Allianz Care</span>
      <span class="cell-insurer__toggle">&#9660;</span>
    </div>
  </td>
  <td class="cell-price cell-price--available">€89/mnd</td>
  <td class="cell-price cell-price--available">€125/mnd</td>
  <td class="cell-price cell-price--available">€156/mnd</td>
</tr>
<!-- Detail rij (verborgen tot klik) -->
<tr class="detail-row" style="display: none;">
  <td colspan="4">
    <!-- HTMX laadt hier de content -->
    <div class="htmx-indicator">
      <div class="spinner"></div>
    </div>
  </td>
</tr>
```

---

## Buttons (alle varianten)

```html
<!-- Primary -->
<button class="btn-primary">Vergelijk verzekeringen</button>

<!-- Primary met pijl -->
<a class="btn-primary-arrow" href="#">Vraag advies</a>

<!-- Secondary / Ghost (op donkere achtergrond) -->
<button class="btn-secondary">Lees verder</button>

<!-- Wit met pijl -->
<a class="btn-arrow-white" href="#">Volg ons stappenplan</a>

<!-- Text link met pijl -->
<a class="btn-text-arrow" href="#">Bekijk alle verzekeraars</a>
```

---

## Input Samenvatting

```html
<div class="card card--summary">
  <div class="summary">
    <span class="summary__text">
      35 jaar, Spanje, met partner en 2 kinderen, 1-2 jaar, werken
    </span>
    <a class="btn-text-arrow" href="/tool">Wijzig gegevens</a>
  </div>
</div>
```

---

## Loading State (HTMX)

```html
<!-- Op element dat content vervangt -->
<div id="results-tables" class="htmx-indicator-parent">
  <!-- Skeleton loaders zichtbaar tijdens laden -->
  <div class="htmx-indicator">
    <div class="skeleton" style="height: 200px; margin-bottom: 20px;"></div>
    <div class="skeleton" style="height: 200px;"></div>
  </div>

  <!-- Tabellen worden hier geladen -->
</div>
```

---

## CSS Classes Overzicht

### Layout
- `.card` — witte kaart met border en radius
- `.card--summary` — grijze samenvatting-kaart
- `.table-container` — horizontaal scrollbare tabel-wrapper
- `.results-section` — sectie met titel en tabel
- `.filters` — filter bar container
- `.filters__group` — groep binnen filters
- `.filters__chips` — chips container

### Formulier
- `.formfield` — veld wrapper (margin-bottom)
- `.formfield__label` — label
- `.formfield__label--required` — met `*` indicator
- `.formfield__input` — text/date input
- `.formfield__select` — dropdown
- `.formfield__radio-group` — radio groep
- `.formfield__radio-label` — radio label
- `.formfield__checkbox-group` — checkbox groep
- `.formfield__checkbox-label` — checkbox label
- `.formfield__helper` — helptekst
- `.formfield__message` — foutmelding
- `.formfield--error` — error state op wrapper
- `.formfield--ok` — succes state op wrapper
- `.form-section__title` — sectie header
- `.form__submit` — submit knop
- `.form__submit--loading` — loading state

### Tabel
- `.result-row` — klikbare data rij
- `.result-row.expanded` — actieve rij
- `.detail-row` — verborgen detail rij
- `.detail-panel` — detail inhoud
- `.cell-insurer` — verzekeraar cel
- `.cell-price` — prijs cel
- `.cell-price--available` — beschikbare prijs
- `.cell-price--unavailable` — niet beschikbaar (✗)
- `.cell-price--website` — "Zie website"

### Buttons
- `.btn-primary` — blauwe gevulde button
- `.btn-primary-arrow` — blauw met pijl
- `.btn-secondary` — transparant met witte border
- `.btn-arrow-white` — wit met pijl
- `.btn-text-arrow` — tekst link met pijl

### Componenten
- `.filter-chip` — filter chip
- `.filter-chip.active` — actieve chip
- `.toggle` — toggle switch
- `.counter` — +/- teller
- `.badge` — status badge
- `.skeleton` — skeleton loader
- `.spinner` — loading spinner

---

*Alle styling verwijst naar de tokens in [design_tokens.md](design_tokens.md).*
