# Visuele Integratie

## Strategie: 3-lagen CSS

| Laag                 | Wat                                 | Bestand        | Bron                |
| -------------------- | ----------------------------------- | -------------- | ------------------- |
| 1. Global theme      | Fonts, kleuren, typografie, buttons | main.css       | expatverzekering.nl |
| 2. Header + Footer   | Navigatie, logo, social, footer     | main.css       | expatverzekering.nl |
| 3. Eigen componenten | Formulier, tabel, chat, filters     | components.css | Zelf bouwen         |

---

## Stap 1: CSS ophalen van expatverzekering.nl

1. Open expatverzekering.nl in Chrome
2. DevTools → Network tab → filter op CSS
3. Identificeer de stylesheet(s)
4. Download en analyseer:
   - Welke fonts worden geladen (@font-face of Google Fonts link)
   - Kleurenpalet (zoek naar veelgebruikte hex-kleuren)
   - Button styles (`.button`, `.button--rounded-blue`)
   - Typografie (body font-size, heading sizes, line-height)

### Te extraheren naar main.css:

- `@font-face` regels of Google Fonts `@import`
- CSS variabelen / kleurwaarden
- Body/html basis styles
- Heading styles (h1-h4)
- Link styles
- Button styles
- Alle `.header-*` classes
- Alle `.footer-*` classes
- Alle `.nav-*` classes
- Alle `.logo-*` classes
- Alle `.social-media*` classes
- Alle `.button-cta` classes

### NIET overnemen:

- Content-specifieke styles (artikelen, blog posts, etc.)
- Pagina-specifieke layouts die we niet gebruiken

---

## Stap 2: Header HTML

Exacte HTML hieronder plakken. **Alle links moeten absoluut zijn** (https://www.expatverzekering.nl/...).

**Let op:**

- Logo afbeeldingen: link naar origineel op expatverzekering.nl OF kopieer lokaal naar static/img/
- JavaScript voor menu toggle: overnemen of herschrijven met Alpine.js
- Zoekfunctie: linken naar expatverzekering.nl/zoeken/ (niet zelf bouwen)

### Header HTML:

```html
<header class="header">
  <div class="header-container">
    <div class="logo-visual">
      <p>
        <span>Homepage</span>
      </p>
    </div>
    <div class="logo-text logo-text--1">
      <p>
        <span>Homepage</span>
      </p>
    </div>
    <div class="header-search-toggle">
      <a href="https://www.expatverzekering.nl/zoeken/" title="Zoeken"
        ><span>Zoeken</span></a
      >
    </div>
    <script>
      document
        .querySelector(".header-search-toggle")
        .addEventListener("click", function (e) {
          e.preventDefault();
          document
            .querySelector(".header")
            .classList.toggle("header-search-opened");
        });
    </script>
    <div class="block-search">
      <form
        role="search"
        method="get"
        action="https://www.expatverzekering.nl/zoeken/"
      >
        <input type="search" id="q" name="q" placeholder="Zoeken" value="" />
        <input class="submit" type="submit" value="OK" />
      </form>
    </div>
    <div class="button-cta">
      <a
        class="button button--rounded-blue"
        href="https://www.expatverzekering.nl/advies/"
        title="Vraag advies"
        >Vraag advies</a
      >
    </div>
    <div class="header-nav-toggle">
      <a href="#header-nav" class="header-nav-toggle-button" title="Menu">
        <span></span><span></span><span></span>
        <span class="header-nav-toggle-text">Menu</span>
      </a>
    </div>
    <script>
      document
        .querySelector(".header-nav-toggle-button")
        .addEventListener("click", function (e) {
          e.preventDefault();
          document
            .querySelector(".header")
            .classList.toggle("header-nav-opened");
        });
    </script>
    <div id="header-nav" class="header-nav-container">
      <div class="header-nav-content">
        <nav class="nav-global" aria-label="Global">
          <div class="nav-global-container">
            <ul>
              <li>
                <a
                  href="https://www.expatverzekering.nl/over-joho-insurances/"
                  title="Over JoHo Insurances"
                  >Over JoHo Insurances</a
                >
              </li>
              <li>
                <a
                  href="https://www.expatverzekering.nl/klantenservice/"
                  title="Klantenservice"
                  >Klantenservice</a
                >
              </li>
            </ul>
          </div>
        </nav>
        <nav class="nav-main" aria-label="Main">
          <div class="nav-main-container">
            <ul class="nav-firstlevel">
              <li class="nav-firstlevel__item nav-firstlevel__item--menu">
                <a
                  class="nav-firstlevel__link"
                  href="https://www.expatverzekering.nl/wie-verzekeren-wij/"
                  title="Wie verzekeren wij?"
                  >Wie verzekeren wij?</a
                >
                <span class="nav-firstlevel__toggle"></span>
                <div class="nav-secondlevel nav-secondlevel--targetaudience">
                  <ul>
                    <li class="nav-secondlevel__item">
                      <a
                        class="nav-secondlevel__link"
                        href="https://www.expatverzekering.nl/wie-verzekeren-wij/expats/"
                        title="Expats"
                      >
                        <img
                          class="nav-secondlevel__visual"
                          src="https://www.expatverzekering.nl/images/uploads/cms_visual_7.svg"
                          width="375"
                          height="375"
                          alt=""
                        />
                        <span class="nav-secondlevel__title">Expats</span>
                      </a>
                    </li>
                    <li class="nav-secondlevel__item">
                      <a
                        class="nav-secondlevel__link"
                        href="https://www.expatverzekering.nl/wie-verzekeren-wij/emigranten/"
                        title="Emigranten"
                      >
                        <img
                          class="nav-secondlevel__visual"
                          src="https://www.expatverzekering.nl/images/uploads/cms_visual_26.svg"
                          width="375"
                          height="375"
                          alt=""
                        />
                        <span class="nav-secondlevel__title">Emigranten</span>
                      </a>
                    </li>
                    <li class="nav-secondlevel__item">
                      <a
                        class="nav-secondlevel__link"
                        href="https://www.expatverzekering.nl/wie-verzekeren-wij/bedrijven/"
                        title="Bedrijven"
                      >
                        <img
                          class="nav-secondlevel__visual"
                          src="https://www.expatverzekering.nl/images/uploads/cms_visual_27.svg"
                          width="375"
                          height="375"
                          alt=""
                        />
                        <span class="nav-secondlevel__title">Bedrijven</span>
                      </a>
                    </li>
                    <li class="nav-secondlevel__item">
                      <a
                        class="nav-secondlevel__link"
                        href="https://www.expatverzekering.nl/wie-verzekeren-wij/digital-nomads/"
                        title="Digital Nomads"
                      >
                        <img
                          class="nav-secondlevel__visual"
                          src="https://www.expatverzekering.nl/images/uploads/cms_visual_25.svg"
                          width="375"
                          height="375"
                          alt=""
                        />
                        <span class="nav-secondlevel__title"
                          >Digital Nomads</span
                        >
                      </a>
                    </li>
                    <li class="nav-secondlevel__item">
                      <a
                        class="nav-secondlevel__link"
                        href="https://www.expatverzekering.nl/wie-verzekeren-wij/pensionados/"
                        title="Pensionado's"
                      >
                        <img
                          class="nav-secondlevel__visual"
                          src="https://www.expatverzekering.nl/images/uploads/cms_visual_28.svg"
                          width="375"
                          height="375"
                          alt=""
                        />
                        <span class="nav-secondlevel__title">Pensionado's</span>
                      </a>
                    </li>
                    <li class="nav-secondlevel__item">
                      <a
                        class="nav-secondlevel__link"
                        href="https://www.expatverzekering.nl/wie-verzekeren-wij/reizen/"
                        title="Reizen"
                      >
                        <img
                          class="nav-secondlevel__visual"
                          src="https://www.expatverzekering.nl/images/uploads/cms_visual_29.svg"
                          width="375"
                          height="375"
                          alt=""
                        />
                        <span class="nav-secondlevel__title">Reizen</span>
                      </a>
                    </li>
                  </ul>
                </div>
              </li>
              <li class="nav-firstlevel__item nav-firstlevel__item--menu">
                <a
                  class="nav-firstlevel__link"
                  href="https://www.expatverzekering.nl/internationale-verzekeringen/"
                  title="Wat verzekeren wij?"
                  >Wat verzekeren wij?</a
                >
                <span class="nav-firstlevel__toggle"></span>
                <div class="nav-secondlevel nav-secondlevel--insurances">
                  <div class="nav-secondlevel--insurances-container">
                    <div class="insurances__list">
                      <ul style="--column-count: 2">
                        <li class="nav-secondlevel__item">
                          <a
                            class="nav-secondlevel__link"
                            href="https://www.expatverzekering.nl/internationale-verzekeringen/ziektekostenverzekering/"
                            title="Ziektekosten"
                          >
                            <span class="nav-secondlevel__title"
                              >Ziektekosten</span
                            >
                          </a>
                        </li>
                        <li class="nav-secondlevel__item">
                          <a
                            class="nav-secondlevel__link"
                            href="https://www.expatverzekering.nl/internationale-verzekeringen/aansprakelijkheid/"
                            title="Aansprakelijkheid"
                          >
                            <span class="nav-secondlevel__title"
                              >Aansprakelijkheid</span
                            >
                          </a>
                        </li>
                        <li class="nav-secondlevel__item">
                          <a
                            class="nav-secondlevel__link"
                            href="https://www.expatverzekering.nl/internationale-verzekeringen/arbeidsongeschiktheid/"
                            title="Arbeidsongeschiktheid"
                          >
                            <span class="nav-secondlevel__title"
                              >Arbeidsongeschiktheid</span
                            >
                          </a>
                        </li>
                        <li class="nav-secondlevel__item">
                          <a
                            class="nav-secondlevel__link"
                            href="https://www.expatverzekering.nl/internationale-verzekeringen/huis-en-inboedel/"
                            title="Huis en inboedel in NL"
                          >
                            <span class="nav-secondlevel__title"
                              >Huis en inboedel in NL</span
                            >
                          </a>
                        </li>
                        <li class="nav-secondlevel__item">
                          <a
                            class="nav-secondlevel__link"
                            href="https://www.expatverzekering.nl/internationale-verzekeringen/inboedel-buitenland/"
                            title="Inboedel in het buitenland"
                          >
                            <span class="nav-secondlevel__title"
                              >Inboedel in het buitenland</span
                            >
                          </a>
                        </li>
                        <li class="nav-secondlevel__item">
                          <a
                            class="nav-secondlevel__link"
                            href="https://www.expatverzekering.nl/internationale-verzekeringen/ongevallenverzekering/"
                            title="Ongevallen"
                          >
                            <span class="nav-secondlevel__title"
                              >Ongevallen</span
                            >
                          </a>
                        </li>
                        <li class="nav-secondlevel__item">
                          <a
                            class="nav-secondlevel__link"
                            href="https://www.expatverzekering.nl/internationale-verzekeringen/overbruggingsverzekering/"
                            title="Overbrugging bij emigratie"
                          >
                            <span class="nav-secondlevel__title"
                              >Overbrugging bij emigratie</span
                            >
                          </a>
                        </li>
                        <li class="nav-secondlevel__item">
                          <a
                            class="nav-secondlevel__link"
                            href="https://www.expatverzekering.nl/internationale-verzekeringen/levensverzekeringen/"
                            title="Overlijdensrisico"
                          >
                            <span class="nav-secondlevel__title"
                              >Overlijdensrisico</span
                            >
                          </a>
                        </li>
                        <li class="nav-secondlevel__item">
                          <a
                            class="nav-secondlevel__link"
                            href="https://www.expatverzekering.nl/internationale-verzekeringen/rechtsbijstand/"
                            title="Rechtsbijstand"
                          >
                            <span class="nav-secondlevel__title"
                              >Rechtsbijstand</span
                            >
                          </a>
                        </li>
                        <li class="nav-secondlevel__item">
                          <a
                            class="nav-secondlevel__link"
                            href="https://www.expatverzekering.nl/internationale-verzekeringen/reis-en-annulering/"
                            title="Reis en annulering"
                          >
                            <span class="nav-secondlevel__title"
                              >Reis en annulering</span
                            >
                          </a>
                        </li>
                        <li class="nav-secondlevel__item">
                          <a
                            class="nav-secondlevel__link"
                            href="https://www.expatverzekering.nl/internationale-verzekeringen/sos/"
                            title="SOS hulpverlening"
                          >
                            <span class="nav-secondlevel__title"
                              >SOS hulpverlening</span
                            >
                          </a>
                        </li>
                        <li class="nav-secondlevel__item">
                          <a
                            class="nav-secondlevel__link"
                            href="https://www.expatverzekering.nl/internationale-verzekeringen/tandheelkunde/"
                            title="Tandheelkunde en Orthodontie"
                          >
                            <span class="nav-secondlevel__title"
                              >Tandheelkunde en Orthodontie</span
                            >
                          </a>
                        </li>
                      </ul>
                    </div>
                    <div class="insurances__inline-menu">
                      <div class="insurances__inline-menu-container">
                        <p>Met deze verzekeraars werken wij samen</p>
                        <ul>
                          <li>
                            <a
                              href="https://www.expatverzekering.nl/internationale-verzekeringen/verzekeraars/acs/"
                              title="ACS"
                              >ACS</a
                            >
                          </li>
                          <li>
                            <a
                              href="https://www.expatverzekering.nl/internationale-verzekeringen/verzekeraars/allianz-care/"
                              title="Allianz Care"
                              >Allianz Care</a
                            >
                          </li>
                          <li>
                            <a
                              href="https://www.expatverzekering.nl/internationale-verzekeringen/verzekeraars/allianz-global-assistance/"
                              title="Allianz Global Assistance"
                              >Allianz Global Assistance</a
                            >
                          </li>
                          <li>
                            <a
                              href="https://www.expatverzekering.nl/internationale-verzekeringen/verzekeraars/april-international/"
                              title="April International"
                              >April International</a
                            >
                          </li>
                          <li>
                            <a
                              href="https://www.expatverzekering.nl/internationale-verzekeringen/verzekeraars/asssa/"
                              title="ASSSA"
                              >ASSSA</a
                            >
                          </li>
                          <li>
                            <a
                              href="https://www.expatverzekering.nl/internationale-verzekeringen/verzekeraars/cigna/"
                              title="Cigna"
                              >Cigna</a
                            >
                          </li>
                          <li>
                            <a
                              href="https://www.expatverzekering.nl/internationale-verzekeringen/verzekeraars/expatriate-group/"
                              title="Expatriate Group"
                              >Expatriate Group</a
                            >
                          </li>
                          <li>
                            <a
                              href="https://www.expatverzekering.nl/internationale-verzekeringen/verzekeraars/globality-health/"
                              title="Globality Health"
                              >Globality Health</a
                            >
                          </li>
                          <li>
                            <a
                              href="https://www.expatverzekering.nl/internationale-verzekeringen/verzekeraars/de-goudse-verzekeringen/"
                              title="Goudse Verzekeringen"
                              >Goudse Verzekeringen</a
                            >
                          </li>
                          <li>
                            <a
                              href="https://www.expatverzekering.nl/internationale-verzekeringen/verzekeraars/henner/"
                              title="Henner"
                              >Henner</a
                            >
                          </li>
                          <li>
                            <a
                              href="https://www.expatverzekering.nl/internationale-verzekeringen/verzekeraars/IMG/"
                              title="IMG"
                              >IMG</a
                            >
                          </li>
                          <li>
                            <a
                              href="https://www.expatverzekering.nl/internationale-verzekeringen/verzekeraars/oom-verzekeringen/"
                              title="OOM Verzekeringen"
                              >OOM Verzekeringen</a
                            >
                          </li>
                          <li>
                            <a
                              href="https://www.expatverzekering.nl/internationale-verzekeringen/verzekeraars/safetywing/"
                              title="SafetyWing"
                              >SafetyWing</a
                            >
                          </li>
                          <li>
                            <a
                              href="https://www.expatverzekering.nl/internationale-verzekeringen/verzekeraars/william-russell/"
                              title="William Russell"
                              >William Russell</a
                            >
                          </li>
                          <li>
                            <a
                              href="https://www.expatverzekering.nl/internationale-verzekeringen/verzekeraars/world-nomads/"
                              title="World Nomads"
                              >World Nomads</a
                            >
                          </li>
                        </ul>
                        <p class="insurances__inline-menu-link">
                          <a
                            class="button button--textual-arrow-black"
                            href="https://www.expatverzekering.nl/internationale-verzekeringen/verzekeraars/"
                            >Bekijk alle verzekeraars</a
                          >
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </li>
              <li class="nav-firstlevel__item nav-firstlevel__item--menu">
                <a
                  class="nav-firstlevel__link"
                  href="https://www.expatverzekering.nl/landen/"
                  title="Landen"
                  >Landen</a
                >
                <span class="nav-firstlevel__toggle"></span>
                <div class="nav-secondlevel nav-secondlevel--default">
                  <ul>
                    <li class="nav-secondlevel__item">
                      <a
                        class="nav-secondlevel__link"
                        href="https://www.expatverzekering.nl/landen/curacao/"
                        title="Naar Curaçao"
                      >
                        <span class="nav-secondlevel__title">Naar Curaçao</span>
                      </a>
                    </li>
                    <li class="nav-secondlevel__item">
                      <a
                        class="nav-secondlevel__link"
                        href="https://www.expatverzekering.nl/landen/dubai/"
                        title="Naar Dubai"
                      >
                        <span class="nav-secondlevel__title">Naar Dubai</span>
                      </a>
                    </li>
                    <li class="nav-secondlevel__item">
                      <a
                        class="nav-secondlevel__link"
                        href="https://www.expatverzekering.nl/landen/frankrijk/"
                        title="Naar Frankrijk"
                      >
                        <span class="nav-secondlevel__title"
                          >Naar Frankrijk</span
                        >
                      </a>
                    </li>
                    <li class="nav-secondlevel__item">
                      <a
                        class="nav-secondlevel__link"
                        href="https://www.expatverzekering.nl/landen/indonesie/"
                        title="Naar Indonesië"
                      >
                        <span class="nav-secondlevel__title"
                          >Naar Indonesië</span
                        >
                      </a>
                    </li>
                    <li class="nav-secondlevel__item">
                      <a
                        class="nav-secondlevel__link"
                        href="https://www.expatverzekering.nl/landen/spanje/"
                        title="Naar Spanje"
                      >
                        <span class="nav-secondlevel__title">Naar Spanje</span>
                      </a>
                    </li>
                    <li class="nav-secondlevel__item">
                      <a
                        class="nav-secondlevel__link"
                        href="https://www.expatverzekering.nl/landen/uk/"
                        title="Naar de UK"
                      >
                        <span class="nav-secondlevel__title">Naar de UK</span>
                      </a>
                    </li>
                    <li class="nav-secondlevel__item">
                      <a
                        class="nav-secondlevel__link"
                        href="https://www.expatverzekering.nl/landen/usa/"
                        title="Naar de USA"
                      >
                        <span class="nav-secondlevel__title">Naar de USA</span>
                      </a>
                    </li>
                    <li class="nav-secondlevel__item">
                      <a
                        class="nav-secondlevel__link"
                        href="https://www.expatverzekering.nl/landen/zweden/"
                        title="Naar Zweden"
                      >
                        <span class="nav-secondlevel__title">Naar Zweden</span>
                      </a>
                    </li>
                    <li class="nav-secondlevel__item">
                      <a
                        class="nav-secondlevel__link"
                        href="https://www.expatverzekering.nl/landen/zwitserland/"
                        title="Naar Zwitserland"
                      >
                        <span class="nav-secondlevel__title"
                          >Naar Zwitserland</span
                        >
                      </a>
                    </li>
                    <li class="nav-secondlevel__item">
                      <a
                        class="nav-secondlevel__link"
                        href="https://www.expatverzekering.nl/landen/wereldwijd/"
                        title="Naar andere landen"
                      >
                        <span class="nav-secondlevel__title"
                          >Naar andere landen</span
                        >
                      </a>
                    </li>
                    <li class="nav-secondlevel__item">
                      <a
                        class="nav-secondlevel__link"
                        href="https://www.expatverzekering.nl/landen/terug-naar-nederland/"
                        title="Terug naar Nederland"
                      >
                        <span class="nav-secondlevel__title"
                          >Terug naar Nederland</span
                        >
                      </a>
                    </li>
                    <li class="nav-secondlevel__item">
                      <a
                        class="nav-secondlevel__link"
                        href="https://www.expatverzekering.nl/landen/bezoek-aan-nederland/"
                        title="Bezoek aan Nederland"
                      >
                        <span class="nav-secondlevel__title"
                          >Bezoek aan Nederland</span
                        >
                      </a>
                    </li>
                  </ul>
                </div>
              </li>
              <li class="nav-firstlevel__item nav-firstlevel__item--default">
                <a
                  class="nav-firstlevel__link"
                  href="https://www.expatverzekering.nl/kennisbank/"
                  title="Kennisbank"
                  >Kennisbank</a
                >
              </li>
              <li class="nav-firstlevel__item nav-firstlevel__item--list">
                <a
                  class="nav-firstlevel__link"
                  href="https://www.expatverzekering.nl/nieuws/"
                  title="Nieuws"
                  >Nieuws</a
                >
              </li>
              <li class="nav-firstlevel__item nav-firstlevel__item--default">
                <a
                  class="nav-firstlevel__link"
                  href="https://www.expatverzekering.nl/verzekeringen/"
                  title="Verzekeringen"
                  >Verzekeringen</a
                >
              </li>
            </ul>
          </div>
        </nav>
        <script>
          var windowWidth =
            window.innerWidth ||
            document.documentElement.clientWidth ||
            document.body.clientWidth;

          document
            .querySelectorAll(
              ".nav-firstlevel__item--menu .nav-firstlevel__link",
            )
            .forEach(function (item) {
              item.addEventListener("click", function (e) {
                if (
                  item.parentNode.classList.contains(
                    "nav-firstlevel__item--opened",
                  ) ||
                  (windowWidth < 1024 &&
                    item.parentNode.classList.contains(
                      "nav-firstlevel__item--selected",
                    ))
                ) {
                  // follow link
                } else {
                  e.preventDefault();

                  // close siblings
                  var siblings = getSiblings(item.parentNode);
                  if (siblings.length) {
                    for (var i = 0; i < siblings.length; i++) {
                      siblings[i].classList.remove(
                        "nav-firstlevel__item--opened",
                      );
                    }
                  }

                  // toggle opened class
                  item.parentNode.classList.toggle(
                    "nav-firstlevel__item--opened",
                  );

                  // show nav secondlevel container for desktop
                  if (windowWidth >= 1024) {
                    // get the container for nav secondlevel
                    var navSecondLevelContainer = document.querySelector(
                      ".nav-secondlevel-container",
                    );

                    if (
                      item.parentNode.classList.contains(
                        "nav-firstlevel__item--opened",
                      )
                    ) {
                      // first empty the container
                      navSecondLevelContainer.innerHTML = "";

                      // copy the secondlevel into it
                      var navSecondLevel = item.parentNode
                        .querySelector(".nav-secondlevel")
                        .cloneNode(true);
                      navSecondLevelContainer.appendChild(navSecondLevel);

                      // set container as opened
                      navSecondLevelContainer.classList.add(
                        "nav-secondlevel-container--opened",
                      );
                    } else {
                      // first empty the container
                      navSecondLevelContainer.innerHTML = "";

                      // set container as closed
                      navSecondLevelContainer.classList.remove(
                        "nav-secondlevel-container--opened",
                      );
                    }
                  }
                }
              });
            });

          document.addEventListener("click", function (e) {
            if (
              e.target &&
              e.target.closest(".nav-firstlevel__item") === null &&
              e.target.closest(".nav-secondlevel-container") === null
            ) {
              // close all menu items
              document
                .querySelectorAll(".nav-firstlevel__item--menu")
                .forEach(function (item) {
                  item.classList.remove("nav-firstlevel__item--opened");
                });

              // get the container for nav secondlevel
              var navSecondLevelContainer = document.querySelector(
                ".nav-secondlevel-container",
              );

              // first empty the container
              navSecondLevelContainer.innerHTML = "";

              // set container as closed
              navSecondLevelContainer.classList.remove(
                "nav-secondlevel-container--opened",
              );
            }
          });

          function getSiblings(element) {
            // Setup siblings array and get the first sibling
            var siblings = [];
            var sibling = element.parentNode.firstChild;

            // Loop through each sibling and push to the array
            while (sibling) {
              if (sibling.nodeType === 1 && sibling !== element) {
                siblings.push(sibling);
              }
              sibling = sibling.nextSibling;
            }

            return siblings;
          }
        </script>
        <div class="button-cta">
          <a
            class="button button--rounded-blue"
            href="https://www.expatverzekering.nl/advies/"
            title="Vraag advies"
            >Vraag advies</a
          >
        </div>
      </div>
    </div>
  </div>
  <div class="nav-secondlevel-container"></div>
</header>
```

---

## Stap 3: Footer HTML

### Footer HTML:

```html
<footer class="footer">
  <div class="footer-interaction">
    <div class="footer-interaction-container">
      <div class="logo-container">
        <div class="logo-text logo-text--1">
          <p>
            <span>Homepage</span>
          </p>
        </div>
        <div class="logo-visual">
          <p>
            <span>Homepage</span>
          </p>
        </div>
      </div>
      <div class="button-cta">
        <a
          class="button button--rounded-blue"
          href="https://www.expatverzekering.nl/advies/"
          title="Vraag advies"
          >Vraag advies</a
        >
      </div>
      <div class="social-media">
        <p class="social-media__title">Volg ons</p>
        <ul class="social-media__list">
          <li class="social-media__item social-media__item--facebook">
            <a
              href="https://nl-nl.facebook.com/JoHoInsurances/"
              title="Facebook"
              target="_blank"
              ><span>Facebook</span></a
            >
          </li>
          <li class="social-media__item social-media__item--linkedin">
            <a
              href="https://nl.linkedin.com/company/joho-insurances"
              title="LinkedIn"
              target="_blank"
              ><span>LinkedIn</span></a
            >
          </li>
        </ul>
      </div>
    </div>
  </div>
  <div class="footer-overview">
    <div class="footer-overview-container">
      <nav class="footer-nav-overview" aria-label="Footer overview">
        <ul class="overview-single">
          <li>
            <p>
              <a
                href="https://www.expatverzekering.nl/internationale-verzekeringen/"
                title="Internationale verzekeringen"
                >Internationale verzekeringen</a
              >
            </p>
          </li>
          <li>
            <p>
              <a
                href="https://www.expatverzekering.nl/kennisbank/"
                title="Kennisbank"
                >Kennisbank</a
              >
            </p>
          </li>
          <li>
            <p>
              <a
                href="https://www.expatverzekering.nl/klantenservice/"
                title="Klantenservice"
                >Klantenservice</a
              >
            </p>
          </li>
        </ul>
        <ul class="overview-double">
          <li>
            <p>
              <a
                href="https://www.expatverzekering.nl/over-joho-insurances/"
                title="Over JoHo Insurances"
                >Over JoHo Insurances</a
              >
            </p>
            <ul>
              <li>
                <p>
                  <a
                    href="https://www.expatverzekering.nl/over-joho-insurances/werken-bij/"
                    title="Werken bij"
                    >Werken bij</a
                  >
                </p>
              </li>
              <li>
                <p>
                  <a
                    target="_blank"
                    href="https://www.joho.org/en"
                    title="The World of JoHo"
                    >The World of JoHo</a
                  >
                </p>
              </li>
            </ul>
          </li>
        </ul>
      </nav>
      <div class="section-contact">
        <h2>
          <a
            href="https://www.expatverzekering.nl/klantenservice/contact/"
            title="Contact"
            >Contact</a
          >
        </h2>
        <p>Stationsweg 2-D, Leiden, Nederland</p>
        <p><a href="tel:+31883214561">+31 88 3214561</a></p>
        <p>
          <a href="mailto:contact@johoinsurances.org"
            >contact@johoinsurances.org</a
          >
        </p>
      </div>
    </div>
  </div>
  <div class="footer-navigation">
    <div class="section-certification">
      <p>
        JoHo Insurances is een door de AFM erkend bemiddelaar (nr. 12043929) in
        verzekeringen.
      </p>
    </div>
    <div class="footer-navigation-container">
      <nav class="nav-footer" aria-label="Footer">
        <ul>
          <li>
            <a
              href="https://www.expatverzekering.nl/disclaimer/"
              title="Disclaimer"
              >Disclaimer</a
            >
          </li>
          <li>
            <a
              href="https://www.expatverzekering.nl/privacyverklaring/"
              title="Privacyverklaring"
              >Privacyverklaring</a
            >
          </li>
          <li>
            <a
              href="https://www.expatverzekering.nl/joho-insurances-algemene-voorwaarden.pdf"
              title="Algemene Voorwaarden"
              >Algemene Voorwaarden</a
            >
          </li>
          <li>
            <a
              href="https://www.expatverzekering.nl/cookiebeleid/"
              title="Cookie beleid"
              >Cookie beleid</a
            >
          </li>
        </ul>
      </nav>
      <div class="section-copyright">
        <p>© 2026 JoHo Insurances</p>
      </div>
    </div>
  </div>
</footer>
```

---

## Stap 4: Fonts identificeren

```css
/* Fonts — exact afgeleid van expatverzekering.nl */
@font-face {
  font-family: "Inter";
  font-style: normal;
  font-weight: 400;
  font-stretch: 100%;
  src:
    url(https://fonts.bunny.net/inter/files/inter-latin-400-normal.woff2)
      format("woff2"),
    url(https://fonts.bunny.net/inter/files/inter-latin-400-normal.woff)
      format("woff");
  unicode-range:
    U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC,
    U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212,
    U+2215, U+FEFF, U+FFFD;
}

@font-face {
  font-family: "Inter";
  font-style: normal;
  font-weight: 500;
  font-stretch: 100%;
  src:
    url(https://fonts.bunny.net/inter/files/inter-latin-500-normal.woff2)
      format("woff2"),
    url(https://fonts.bunny.net/inter/files/inter-latin-500-normal.woff)
      format("woff");
  unicode-range:
    U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC,
    U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212,
    U+2215, U+FEFF, U+FFFD;
}

@font-face {
  font-family: "Inter";
  font-style: normal;
  font-weight: 600;
  font-stretch: 100%;
  src:
    url(https://fonts.bunny.net/inter/files/inter-latin-600-normal.woff2)
      format("woff2"),
    url(https://fonts.bunny.net/inter/files/inter-latin-600-normal.woff)
      format("woff");
  unicode-range:
    U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC,
    U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212,
    U+2215, U+FEFF, U+FFFD;
}

@font-face {
  font-family: "Inter";
  font-style: normal;
  font-weight: 700;
  font-stretch: 100%;
  src:
    url(https://fonts.bunny.net/inter/files/inter-latin-700-normal.woff2)
      format("woff2"),
    url(https://fonts.bunny.net/inter/files/inter-latin-700-normal.woff)
      format("woff");
  unicode-range:
    U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC,
    U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212,
    U+2215, U+FEFF, U+FFFD;
}
```

---

## Stap 5: Kleurenpalet documenteren

```css
:root {
  --color-primary: #0072da;
  --color-secondary: #f8f4e7;

  --color-text: #000000;
  --color-text-light: #666666;

  --color-background: #ffffff;
  --color-background-soft: #f8f4e7;

  --color-border: #e5e5e5;

  --color-success: #2e7d32;
  --color-error: #c62828;
}
```

---

## Stap 5b: Header & Footer CSS (main.css)

**VOORDAT je main.css schrijft:**

1. Open https://www.expatverzekering.nl/ via Chrome DevTools MCP
2. Inspecteer de volgende elementen en extraheer de Computed CSS waarden:

**Header:**

- `.header` → background-color, border-bottom, position, height
- `.header-container` → max-width, padding, display, height, gap
- `.logo-visual p` → width, height, background-image (volledige URL)
- `.logo-text--1 p` → width, height, background-image (volledige URL)
- `.nav-firstlevel__link` → font-family, font-size, font-weight, color, padding
- `.nav-secondlevel` → background, border, box-shadow, border-radius, padding
- `.nav-secondlevel__visual` → width, height
- `.button--rounded-blue` → background-color, color, border-radius, padding, font-size, font-weight
- `.header-search-toggle a` → width, height, icoon-implementatie

**Footer:**

- `.footer` → background-color
- `.footer-interaction` → padding, border-bottom
- `.footer-interaction-container` → max-width, padding, display, gap
- `.footer-overview-container` → max-width, padding, display, gap
- `.footer-navigation` → background-color, padding, border-top
- `.social-media__item a` → width, height, border-radius, background-color, icoon-type
- `.nav-footer a` → font-size, color
- `.section-copyright p` → font-size, color

**Global:**

- `body` → font-family, font-size, line-height, color
- `h1`, `h2`, `h3` → font-size, font-weight, line-height
- `a` → color, text-decoration

3. Schrijf main.css UITSLUITEND op basis van deze gemeten waarden
4. VERZIN GEEN waarden — als iets niet te meten is, laat het weg

## Stap 6: Eigen componenten stylen (components.css)

Gebruik dezelfde fonts, kleuren en button-styles als de hoofdsite (zie Stap 4 en 5).

### Te stylen componenten (zie fase2_vergelijkingstool.md):

- Formulier: inputs, labels, selects, date pickers, toggles, tellers
- Samenvatting banner ("35 jaar, Spanje, met partner...")
- Filter: eigen risico dropdown + coverage checkboxes
- Resultaten tabel: rijen, kolommen, hover states
- Uitklapbare rij: detail onder verzekeraar-rij
- Loading states (bij HTMX swaps)
- Error states (validatie + API fouten)
- Chat sectie (stub, fase 3)

### Instructie voor AI agent:

1. Meet eerst de site-styles via DevTools MCP (Stap 5b)
2. Gebruik dezelfde font-family, kleuren, border-radius en
   button-styles als basis voor alle componenten
3. Houd de styling simpel en consistent met de hoofdsite
4. Geen externe UI libraries — puur CSS passend bij het thema

Bespreek voordat we complexere buttons/dropdown/tables gaan maken eerst met mij online eventueel stijlen/themas/voor geprogrammeerde setups te vinden.

---

## Aandachtspunten

- **Afbeeldingen in header/footer**: SVG's worden waarschijnlijk via `/images/uploads/` geladen. Link absoluut naar `https://www.expatverzekering.nl/images/uploads/...` of kopieer lokaal.
- **Favicon**: kopieer van expatverzekering.nl naar static/img/
- **Menu JavaScript**: de header bevat inline `<script>` tags voor menu toggle. (laat ze staan)
- **Responsive**: de header heeft al responsive gedrag (hamburger menu). Dit moet meegenomen worden.
- **Actieve navigatie**: op de tool-pagina is geen menu-item "actief". Dat is ok.

---

## TODO: Exacte details nog toe te voegen

- [x] Exacte header HTML met absolute links
- [x] Exacte footer HTML met absolute links
- [x] Font identificatie (naam + bron)
- [x] Kleurenpalet (hex waarden invullen)
- [ ] Screenshot van gewenst eindresultaat (wordt toegevoegd na eerste werkende versie)
