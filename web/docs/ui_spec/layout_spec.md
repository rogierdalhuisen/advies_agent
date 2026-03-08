# Layout Specificatie

---

## Globale layout

### Header (fixed)

- **Positie:** `position: fixed; z-index: 20`
- **Hoogte:** 130px (inclusief nav-bar)
- **Achtergrond:** wit (`#FFF`)
- **Border:** `1px solid rgb(227, 235, 238)` onderaan
- **Padding:** `23px 0 0`
- **Container max-width:** 1220px, gecentreerd

**Opbouw:**
```
┌────────────────────────────────────────────────────────────────┐
│ nav-global: 25px hoog, rechts uitgelijnd                       │
│ "Over JoHo Insurances" | "Klantenservice"                      │
├────────────────────────────────────────────────────────────────┤
│ Logo (links) | expatverzekering.nl (midden) | Zoeken | Advies │
│ hoogte ~70px                                                   │
├────────────────────────────────────────────────────────────────┤
│ nav-main: 36px, zwart (#000), witte tekst                      │
│ Links: Wie verzekeren wij? | Wat verzekeren wij? | Landen |... │
└────────────────────────────────────────────────────────────────┘
```

### Footer

Drie secties, elk full-width met eigen achtergrondkleur:

```
┌────────────────────────────────────────────────────────────────┐
│ footer-interaction — rgb(0, 114, 218) (#0072DA)                │
│ Logo's + "Volg ons" social icons + "Vraag advies" button       │
│ padding: 10px 0 0                                              │
├────────────────────────────────────────────────────────────────┤
│ footer-overview — rgb(0, 86, 166) (#0056A6)                    │
│ Sitelinks: Verzekeringen | Over JoHo | Contact                 │
│ Font: 14px semibold (headers), 12px regular (links)            │
│ Kleur: wit                                                     │
│ padding: 0 0 14px                                              │
├────────────────────────────────────────────────────────────────┤
│ footer-navigation — rgb(0, 46, 89) (#002E59)                   │
│ Juridische links, copyright                                    │
│ Font: 12px regular, wit                                        │
└────────────────────────────────────────────────────────────────┘
```

### Content area

- **Main padding-top:** 166px (ruimte voor fixed header + nav)
- **Max-width:** 1260px
- **Padding links/rechts:** 20px
- **Margin:** `0 auto` (gecentreerd)

---

## Pagina: /tool (Formulierpagina)

```
┌────────────────────────────────────────────────────────────────┐
│ HEADER (fixed, 130px)                                          │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Paginatitel (h1, Zilla Slab 48px)                        │  │
│  │ "Vergelijk internationale verzekeringen"                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ FORMULIER CARD                                           │  │
│  │ Achtergrond: wit                                         │  │
│  │ Border: 1px solid var(--color-grey)                      │  │
│  │ Border-radius: 20px                                      │  │
│  │ Padding: 40px                                            │  │
│  │ Max-width: 720px                                         │  │
│  │                                                          │  │
│  │ ┌──────────────────────────────────────────────────────┐  │  │
│  │ │ Sectie header (h2, Poppins 24px 600)                │  │  │
│  │ │ "Uw gegevens"                                       │  │  │
│  │ │ border-bottom: 2px solid var(--color-blue-primary)  │  │  │
│  │ └──────────────────────────────────────────────────────┘  │  │
│  │                                                          │  │
│  │ [geboortedatum] [nationaliteit] [bestemmingsland]        │  │
│  │ [vertrekdatum]  [duur] [hoofdreden]                      │  │
│  │                                                          │  │
│  │ ┌──────────────────────────────────────────────────────┐  │  │
│  │ │ "Gezinssamenstelling"                                │  │  │
│  │ └──────────────────────────────────────────────────────┘  │  │
│  │ [partner toggle] [partner geboortedatum]                 │  │
│  │ [kinderen teller] [kind geboortedatums]                  │  │
│  │                                                          │  │
│  │ [SUBMIT BUTTON — full width]                             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│ FOOTER                                                         │
└────────────────────────────────────────────────────────────────┘
```

**Formulier layout:**
- Velden stapelen verticaal (1 kolom)
- Spacing tussen velden: 24px
- Labels boven velden: margin-bottom 8px
- Sectie headers: margin-bottom 20px, margin-top 40px

---

## Pagina: /tool/resultaten (Resultatenpagina)

```
┌────────────────────────────────────────────────────────────────┐
│ HEADER (fixed, 130px)                                          │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ INPUT SAMENVATTING                                       │  │
│  │ "35 jaar, Spanje, met partner en 2 kinderen"             │  │
│  │ Achtergrond: var(--color-grey-light)                     │  │
│  │ Padding: 20px 30px                                       │  │
│  │ Border-radius: 20px                                      │  │
│  │ Font: 16px Poppins                                       │  │
│  │ [Wijzig gegevens] link rechts                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ FILTERS                                                  │  │
│  │ Eigen risico: [dropdown]                                 │  │
│  │ Dekking: [chip] [chip] [chip] [chip]                     │  │
│  │ Sorteer: [dropdown]                                      │  │
│  │ Padding: 20px 0                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ SECTIE: Internationale Ziektekostenverzekeringen         │  │
│  │ h2, Poppins 24px 600                                     │  │
│  │ ┌──────────────────────────────────────────────────────┐  │  │
│  │ │ TABEL — full width                                  │  │  │
│  │ │ border-radius: 20px                                 │  │  │
│  │ │ box-shadow: 0 0 0 1px var(--color-grey)             │  │  │
│  │ │ Header row: grijs achtergrond                       │  │  │
│  │ │ Data rows: wit, hover: var(--color-grey-light)      │  │  │
│  │ │ Uitklapbare detail onder elke rij                   │  │  │
│  │ └──────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ SECTIE: Internationale Reisverzekeringen                 │  │
│  │ (zelfde opbouw als hierboven)                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ CHAT SECTIE (stub)                                       │  │
│  │ Vast blok, 400px hoogte                                  │  │
│  │ margin-top: 40px                                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│ FOOTER                                                         │
└────────────────────────────────────────────────────────────────┘
```

**Grid/spacing regels:**
- Tabel secties: margin-bottom 40px
- Content max-width: 1260px, padding 0 20px
- Filters en samenvatting: margin-bottom 30px

---

*Zie [design_tokens.md](design_tokens.md) voor exacte waarden.*
