# Form Specificatie

---

## Input Velden

### Text / Date / Email

```css
.formfield {
  margin-bottom: 24px;
}
.formfield__label {
  display: block;
  font-family: Poppins, sans-serif;
  font-size: 18px;
  font-weight: 400;
  color: #000;
  margin-bottom: 8px;
}
.formfield__input {
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
.formfield__input::placeholder {
  color: rgb(var(--color-grey-placeholder)); /* #BEC4C6 */
}
.formfield__input:focus {
  outline: none;
  border-color: rgb(var(--color-blue-primary));
}
```

---

## Dropdowns

```css
.formfield__select {
  font-family: Poppins, sans-serif;
  font-size: 16px;
  height: 40px;
  padding: 7px 40px 7px 20px;
  border: 1px solid rgb(var(--color-grey));
  border-radius: 30px;
  background-color: #FFF;
  color: #000;
  width: 100%;
  appearance: none;
  cursor: pointer;
  /* Chevron-down SVG als achtergrond */
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%23000' stroke-width='1.5' fill='none'/%3E%3C/svg%3E");
  background-position: right 15px center;
  background-repeat: no-repeat;
  background-size: 12px;
}
.formfield__select:focus {
  outline: none;
  border-color: rgb(var(--color-blue-primary));
}
```

---

## Radio Buttons

```css
.formfield__radio-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.formfield__radio-label {
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: Poppins, sans-serif;
  font-size: 18px;
  font-weight: 400;
  color: #000;
  cursor: pointer;
}
.formfield__radio-label input[type="radio"] {
  width: 18px;
  height: 18px;
  accent-color: rgb(var(--color-blue-primary));
}
```

---

## Checkboxes (multi-select)

```css
.formfield__checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}
.formfield__checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: Poppins, sans-serif;
  font-size: 16px;
  color: #000;
  cursor: pointer;
}
.formfield__checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: rgb(var(--color-blue-primary));
}
```

---

## Labels

```css
.formfield__label {
  font-family: Poppins, sans-serif;
  font-size: 18px;
  font-weight: 400;
  color: #000;
  margin-bottom: 8px;
  display: block;
}
/* Verplicht veld indicator */
.formfield__label--required::after {
  content: " *";
  color: rgb(var(--color-red));
}
```

---

## Helper Text

```css
.formfield__helper {
  font-size: 14px;
  color: rgb(var(--color-grey-placeholder));
  margin-top: 6px;
}
```

---

## Validation States

### Error

```css
.formfield--error .formfield__input {
  border-color: rgb(var(--color-red)); /* #D92016 */
  color: rgb(var(--color-red));
  /* Kruis-icoon rechts */
  background-image: url("/assets/joho-1.0.94/images/cross-red.svg");
  background-position: right 20px center;
  background-size: 16px;
  background-repeat: no-repeat;
}
.formfield--error .formfield__message {
  font-size: 12px; /* 1.2rem in origineel */
  color: rgb(var(--color-red));
  margin-top: 10px;
}
```

### Success / OK

```css
.formfield--ok .formfield__input {
  border-color: rgb(var(--color-green)); /* #008C35 */
  color: rgb(var(--color-green));
  /* Check-icoon rechts */
  background-image: url("/assets/joho-1.0.94/images/check-green.svg");
  background-position: right 20px center;
  background-size: 16px;
  background-repeat: no-repeat;
}
```

### Empty (default)

```css
.formfield--empty .formfield__input {
  /* Grijs check-icoon rechts */
  background-image: url("/assets/joho-1.0.94/images/check-grey.svg");
  background-position: right 20px center;
  background-size: 16px;
  background-repeat: no-repeat;
}
```

---

## Sectie Headers (in formulier)

```css
.form-section__title {
  font-family: Poppins, sans-serif;
  font-size: 24px;
  font-weight: 600;
  color: rgb(var(--color-blue-primary)); /* #0072DA */
  border-bottom: 2px solid rgb(var(--color-blue-primary));
  padding-bottom: 10px;
  margin-bottom: 20px;
  margin-top: 40px;
}
.form-section__title:first-child {
  margin-top: 0;
}
```

---

## Submit Knop

```css
.form__submit {
  font-family: Poppins, sans-serif;
  font-size: 16px;
  font-weight: 500;
  color: #FFF;
  background-color: rgb(var(--color-blue-primary));
  border: 1px solid rgb(var(--color-blue-primary));
  border-radius: 30px;
  padding: 13px 52px 12px 30px;
  cursor: pointer;
  width: 100%;
  margin-top: 30px;
  box-shadow: 0 4px 8px rgba(var(--color-blue-primary), 0.3),
              0 0 4px rgba(var(--color-blue-primary), 0.2);
  transition: box-shadow 0.2s ease;
}
.form__submit:hover {
  box-shadow: 0 1px 2px rgba(var(--color-blue-primary), 0.3),
              0 0 4px rgba(var(--color-blue-primary), 0.2);
}
```

---

## Loading State (submit)

```css
.form__submit--loading {
  pointer-events: none;
  opacity: 0.7;
  position: relative;
}
.form__submit--loading::after {
  content: "";
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #FFF;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  margin-left: 10px;
  vertical-align: middle;
}
```

---

## Toggle (Partner ja/nee)

```css
.toggle {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}
.toggle__switch {
  width: 48px;
  height: 26px;
  background: rgb(var(--color-grey-medium));
  border-radius: 13px;
  position: relative;
  transition: background 0.2s ease;
}
.toggle__switch::after {
  content: "";
  width: 22px;
  height: 22px;
  background: #FFF;
  border-radius: 50%;
  position: absolute;
  top: 2px;
  left: 2px;
  transition: transform 0.2s ease;
}
.toggle--active .toggle__switch {
  background: rgb(var(--color-blue-primary));
}
.toggle--active .toggle__switch::after {
  transform: translateX(22px);
}
.toggle__label {
  font-size: 18px;
  font-weight: 400;
}
```

---

## Kinderen Teller

```css
.counter {
  display: flex;
  align-items: center;
  gap: 16px;
}
.counter__btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid rgb(var(--color-grey));
  background: #FFF;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: rgb(var(--color-blue-primary));
}
.counter__btn:hover {
  border-color: rgb(var(--color-blue-primary));
}
.counter__value {
  font-size: 18px;
  font-weight: 600;
  min-width: 24px;
  text-align: center;
}
```

---

*Zie [design_tokens.md](design_tokens.md) voor kleuren en spacing.*
