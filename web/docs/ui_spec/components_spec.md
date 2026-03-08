# Components Specificatie

Alle componenten volgen de design tokens uit [design_tokens.md](design_tokens.md).

---

## Buttons

### Primary (`.button--rounded-blue`)

```css
.btn-primary {
  font-family: Poppins, sans-serif;
  font-size: 14px;
  font-weight: 400;
  color: #FFF;
  background-color: rgb(var(--color-blue-primary)); /* #0072DA */
  border: 1px solid rgb(var(--color-blue-primary));
  border-radius: 30px;
  padding: 9px 30px 8px;
  line-height: 21px;
  cursor: pointer;
  box-shadow: 0 4px 8px rgba(var(--color-blue-primary), 0.3),
              0 0 4px rgba(var(--color-blue-primary), 0.2);
  transition: box-shadow 0.2s ease;
}
.btn-primary:hover {
  box-shadow: 0 1px 2px rgba(var(--color-blue-primary), 0.3),
              0 0 4px rgba(var(--color-blue-primary), 0.2);
}
```

### Primary Arrow (`.button--arrow-rounded-blue`)

Zelfde als primary, maar met pijl-icoon rechts:

```css
.btn-primary-arrow {
  /* ...zelfde als primary... */
  padding: 11px 52px 11px 30px;
  font-size: 16px;
  /* Pijl via ::after pseudo-element of inline SVG */
}
```

### Secondary / Ghost (`.button--border-rounded-white`)

```css
.btn-secondary {
  font-family: Poppins, sans-serif;
  font-size: 16px;
  font-weight: 400;
  color: #FFF;
  background-color: transparent;
  border: 1px solid #FFF;
  border-radius: 30px;
  padding: 12px 30px;
  cursor: pointer;
}
.btn-secondary:hover {
  background-color: rgb(var(--color-blue-primary));
  color: #FFF;
  border-color: rgb(var(--color-blue-primary));
}
```

### Arrow White (`.button--arrow-rounded-white`)

```css
.btn-arrow-white {
  font-family: Poppins, sans-serif;
  font-size: 16px;
  font-weight: 500;
  color: rgb(var(--color-blue-dark)); /* #002E59 */
  background-color: #FFF;
  border: 1px solid #FFF;
  border-radius: 30px;
  padding: 13px 52px 12px 30px;
  cursor: pointer;
}
.btn-arrow-white:hover {
  background-color: rgb(var(--color-blue-primary));
  color: #FFF;
  border-color: rgb(var(--color-blue-primary));
}
```

### Text Link Arrow (`.button--textual-arrow-black`)

```css
.btn-text-arrow {
  font-size: 14px;
  font-weight: 400;
  color: #000;
  background: transparent;
  border: none;
  padding: 0 20px 0 0;
  text-decoration: underline;
  cursor: pointer;
  /* Pijl via ::after of background-image */
}
```

---

## Inputs

### Text Input

```css
.input-text {
  font-family: Poppins, sans-serif;
  font-size: 16px;
  height: 40px;
  padding: 7px 20px;
  border: 1px solid rgb(var(--color-grey)); /* #E3EBEE */
  border-radius: 30px;
  background-color: #FFF;
  color: #000;
  width: 100%;
  box-sizing: border-box;
}
.input-text::placeholder {
  color: rgb(var(--color-grey-placeholder)); /* #BEC4C6 */
}
.input-text:focus {
  outline: none;
  border-color: rgb(var(--color-blue-primary));
}
```

### Date Input

Zelfde als text input. Gebruikt native date picker of tekst-veld met masker.

### Textarea

```css
.input-textarea {
  font-family: Poppins, sans-serif;
  font-size: 18px;
  padding: 20px;
  border: 1px solid rgb(var(--color-grey));
  border-radius: 20px;
  background-color: #FFF;
  color: #000;
  width: 100%;
  min-height: 120px;
  resize: vertical;
}
```

---

## Dropdowns / Selects

```css
.input-select {
  font-family: Poppins, sans-serif;
  font-size: 16px;
  padding: 7px 40px 7px 20px;
  border: 1px solid rgb(var(--color-grey));
  border-radius: 30px;
  background-color: #FFF;
  color: #000;
  appearance: none;
  /* Chevron icon via background-image */
  background-image: url("data:image/svg+xml,..."); /* chevron-down */
  background-position: right 15px center;
  background-repeat: no-repeat;
  background-size: 12px;
  cursor: pointer;
}
.input-select:focus {
  outline: none;
  border-color: rgb(var(--color-blue-primary));
}
```

---

## Filter Chips

Coverage filter checkboxes als chips:

```css
.filter-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: 1px solid rgb(var(--color-grey));
  border-radius: 30px;
  background: #FFF;
  font-family: Poppins, sans-serif;
  font-size: 14px;
  color: #000;
  cursor: pointer;
  transition: all 0.15s ease;
}
.filter-chip:hover {
  border-color: rgb(var(--color-blue-primary));
}
.filter-chip.active {
  background-color: rgb(var(--color-blue-primary));
  color: #FFF;
  border-color: rgb(var(--color-blue-primary));
}
```

---

## Cards

Formulier-card en samenvatting-card:

```css
.card {
  background: #FFF;
  border: 1px solid rgb(var(--color-grey));
  border-radius: 20px;
  padding: 40px;
}
.card--summary {
  background: rgb(var(--color-grey-light)); /* #F2F6F7 */
  padding: 20px 30px;
}
```

---

## Detail Panel (uitklapbare rij)

```css
.detail-panel {
  background: rgb(var(--color-grey-light)); /* #F2F6F7 */
  padding: 20px 30px;
  border-top: 1px solid rgb(var(--color-grey));
  /* Geen eigen border-radius — zit binnen tabel */
}
```

---

## Loading States

```css
/* Skeleton loader */
.skeleton {
  background: linear-gradient(90deg,
    rgb(var(--color-grey-light)) 25%,
    rgb(var(--color-grey)) 50%,
    rgb(var(--color-grey-light)) 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
  border-radius: 20px;
}
@keyframes skeleton-loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Spinner */
.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid rgb(var(--color-grey));
  border-top-color: rgb(var(--color-blue-primary));
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* HTMX loading indicator */
.htmx-indicator {
  opacity: 0;
  transition: opacity 0.2s ease;
}
.htmx-request .htmx-indicator {
  opacity: 1;
}
```

---

## Hover States

| Element        | Hover effect                                              |
|----------------|-----------------------------------------------------------|
| Primary button | box-shadow verkleint (naar 1px 2px)                       |
| Ghost button   | achtergrond wordt blauw, tekst wit                        |
| Tabel rij      | achtergrond: `var(--color-grey-light)`                    |
| Links          | kleur blijft, underline                                   |
| Filter chips   | border wordt blauw                                        |

---

## Focus States

```css
/* Globale focus reset (van expatverzekering.nl) */
a:focus, a:hover, a:active {
  outline: none;
}

/* Eigen focus — gebruik voor toegankelijkheid */
.input-text:focus,
.input-select:focus,
.input-textarea:focus {
  outline: none;
  border-color: rgb(var(--color-blue-primary));
}
button:focus-visible {
  outline: 2px solid rgb(var(--color-blue-primary));
  outline-offset: 2px;
}
```

---

## Badges

Coverage status badges in de tabel:

```css
.badge {
  display: inline-block;
  font-size: 12px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 10px;
}
.badge--available {
  background: rgba(var(--color-green), 0.1);
  color: rgb(var(--color-green));
}
.badge--unavailable {
  background: rgba(var(--color-red), 0.1);
  color: rgb(var(--color-red));
}
.badge--website {
  background: rgba(var(--color-blue-primary), 0.1);
  color: rgb(var(--color-blue-primary));
}
```

---

*Alle kleuren gebruiken de CSS custom properties uit design_tokens.md.*
