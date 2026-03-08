# Design Tokens — expatverzekering.nl

Exacte waarden geextraheerd via Chrome DevTools computed CSS op 8 maart 2026.

---

## CSS Custom Properties (uit :root)

```css
:root {
  --color-yellow-grey:    230, 216, 172;
  --color-beige:          248, 244, 231;
  --color-beige-light:    253, 251, 247;
  --color-blue-primary:   0, 114, 218;
  --color-blue-light:     67, 148, 223;
  --color-blue-medium:    0, 86, 166;
  --color-blue-harmony:   14, 11, 230;
  --color-blue-dark:      0, 46, 89;
  --color-grey-dark:      227, 235, 238;
  --color-grey:           227, 235, 238;
  --color-grey-medium:    217, 221, 222;
  --color-grey-light:     242, 246, 247;
  --color-red:            217, 32, 22;
  --color-green:          0, 140, 53;
  --color-grey-placeholder: 190, 196, 198;
  --color-white:          255, 255, 255;
  --color-black:          0, 0, 0;
  --color-green-chat:     37, 211, 102;
}
```

**Gebruik:** `rgb(var(--color-blue-primary))` = `rgb(0, 114, 218)`

---

## Kleuren — snelreferentie

| Token                  | RGB                   | Hex       | Gebruik                              |
|------------------------|-----------------------|-----------|--------------------------------------|
| `--color-blue-primary` | `rgb(0, 114, 218)`    | `#0072DA` | Primaire kleur, buttons, links, CTA  |
| `--color-blue-light`   | `rgb(67, 148, 223)`   | `#4394DF` | Hover-accent, lichtere varianten     |
| `--color-blue-medium`  | `rgb(0, 86, 166)`     | `#0056A6` | Footer midden-sectie                 |
| `--color-blue-dark`    | `rgb(0, 46, 89)`      | `#002E59` | Footer onderste sectie, donker text  |
| `--color-beige`        | `rgb(248, 244, 231)`  | `#F8F4E7` | Cookie-bar, lichte achtergrond       |
| `--color-beige-light`  | `rgb(253, 251, 247)`  | `#FDFBF7` | Lichtste beige variant               |
| `--color-grey`         | `rgb(227, 235, 238)`  | `#E3EBEE` | Borders, scheidingslijnen            |
| `--color-grey-medium`  | `rgb(217, 221, 222)`  | `#D9DDDE` | Tabel-achtergrond, zwaardere border  |
| `--color-grey-light`   | `rgb(242, 246, 247)`  | `#F2F6F7` | Lichte achtergrond secties           |
| `--color-grey-placeholder` | `rgb(190, 196, 198)` | `#BEC4C6` | Placeholder tekst               |
| `--color-red`          | `rgb(217, 32, 22)`    | `#D92016` | Foutmeldingen, validatie-error       |
| `--color-green`        | `rgb(0, 140, 53)`     | `#008C35` | Succes, validatie-ok                 |
| `--color-black`        | `rgb(0, 0, 0)`        | `#000000` | Body tekst                           |
| `--color-white`        | `rgb(255, 255, 255)`  | `#FFFFFF` | Achtergrond, witte tekst             |

---

## Fonts

### Font families

| Font         | Gebruik                                    | Gewichten             |
|--------------|--------------------------------------------|-----------------------|
| **Poppins**  | Body, navigatie, buttons, labels, paragraaf | 400 (regular), 500 (medium), 600 (semibold) + italic varianten |
| **Zilla Slab** | H1 headings (hero, paginatitels)         | 600 (semibold), 700 (bold) |

### Font-face bronnen

```css
@font-face {
  font-family: Poppins;
  src: url("https://www.expatverzekering.nl/assets/joho-1.0.94/fonts/Poppins-Regular.woff2") format("woff2"),
       url("https://www.expatverzekering.nl/assets/joho-1.0.94/fonts/Poppins-Regular.woff") format("woff");
  font-weight: normal;
}
@font-face {
  font-family: Poppins;
  src: url("https://www.expatverzekering.nl/assets/joho-1.0.94/fonts/Poppins-Medium.woff2") format("woff2");
  font-weight: 500;
}
@font-face {
  font-family: Poppins;
  src: url("https://www.expatverzekering.nl/assets/joho-1.0.94/fonts/Poppins-SemiBold.woff2") format("woff2");
  font-weight: 600;
}
@font-face {
  font-family: Poppins;
  src: url("https://www.expatverzekering.nl/assets/joho-1.0.94/fonts/Poppins-Italic.woff2") format("woff2");
  font-weight: normal;
  font-style: italic;
}
@font-face {
  font-family: Poppins;
  src: url("https://www.expatverzekering.nl/assets/joho-1.0.94/fonts/Poppins-SemiBoldItalic.woff2") format("woff2");
  font-weight: 600;
  font-style: italic;
}
@font-face {
  font-family: "Zilla Slab";
  src: url("https://www.expatverzekering.nl/assets/joho-1.0.94/fonts/ZillaSlab-SemiBold.woff2") format("woff2");
  font-weight: 600;
}
@font-face {
  font-family: "Zilla Slab";
  src: url("https://www.expatverzekering.nl/assets/joho-1.0.94/fonts/ZillaSlab-Bold.woff2") format("woff2");
  font-weight: bold;
}
```

---

## Font Scale (typografie)

| Element    | Font-family           | Size   | Weight | Line-height | Color             |
|------------|-----------------------|--------|--------|-------------|-------------------|
| body       | Poppins, sans-serif   | 18px   | 400    | 28.8px (1.6)| `#000`            |
| h1 (hero)  | "Zilla Slab"          | 48px   | 700    | 57.6px (1.2)| wit of zwart      |
| h1 (content)| "Zilla Slab"         | 48px   | 600    | 57.6px (1.2)| `#000`            |
| h2         | Poppins               | 24px   | 600    | 28.8px (1.2)| `#000`            |
| h3         | Poppins               | 14px   | 600    | 16.8px (1.2)| `#000`            |
| paragraph  | Poppins               | 18px   | 400    | 28.8px (1.6)| `#000`            |
| nav main   | Poppins               | 14px   | 500    | —           | `#FFF`            |
| nav global | Poppins               | 18px   | 400    | —           | `#000`            |
| label      | Poppins               | 18px   | 400    | —           | `#000`            |
| small/meta | Poppins               | 12px   | 400    | —           | `#000`            |

---

## Spacing Scale

| Token     | Waarde | Gebruik                          |
|-----------|--------|----------------------------------|
| `xs`      | 5px    | Inline spacing, kleine gaps      |
| `sm`      | 10px   | Social media icons gap           |
| `md`      | 15px   | Tabel cel padding                |
| `lg`      | 20px   | Content margins, tabel cel padding horizontaal, input padding |
| `xl`      | 30px   | Paragraph margin, button padding, sectie spacing |
| `2xl`     | 40px   | Grotere sectie-gaps              |
| `3xl`     | 60px   | Content padding                  |
| `4xl`     | 80px   | Footer/content padding           |

---

## Border Radius

| Element            | Radius |
|--------------------|--------|
| Buttons (rounded)  | 30px   |
| Inputs / selects   | 30px   |
| Tabellen           | 20px   |
| Search input       | 24px   |
| Cards / content blocks | 20px |

---

## Shadows

```css
/* Primaire button */
.button--rounded-blue {
  box-shadow: 0 4px 8px rgba(var(--color-blue-primary), 0.3),
              0 0 4px rgba(var(--color-blue-primary), 0.2);
}
.button--rounded-blue:hover {
  box-shadow: 0 1px 2px rgba(var(--color-blue-primary), 0.3),
              0 0 4px rgba(var(--color-blue-primary), 0.2);
}

/* Tabel */
table {
  box-shadow: 0 0 0 1px rgb(var(--color-grey));
}
```

---

## Container Widths

| Context              | Max-width |
|----------------------|-----------|
| Header container     | 1220px    |
| Content area (main)  | 1260px    |
| Content padding      | 20px (links/rechts) |

---

## Breakpoints

De site gebruikt een mobile-first responsive benadering.
Het stylesheet laadt als `home.css` op de homepagina.
Exacte breakpoints worden bepaald bij implementatie; gebruik de containerwidths als richtlijn.

| Label    | Indicatief |
|----------|------------|
| Mobile   | < 768px    |
| Tablet   | 768-1024px |
| Desktop  | > 1024px   |

---

*Bron: https://www.expatverzekering.nl/ — stylesheet versie joho-1.0.94*
