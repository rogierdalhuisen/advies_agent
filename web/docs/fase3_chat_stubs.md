# Fase 3: Chat & Uitbreidingen (Stubs)

## Doel

Nu alleen de **aansluitpunten** bouwen. De AI-implementatie komt later.

---

## Chat UI Design

### Weergave
- Vast blok onderaan de resultatenpagina (altijd zichtbaar)
- Chat-stijl: bubbels (klant rechts, AI links)
- Vaste hoogte (bijv. 400px), scrollbaar
- Invoerveld onderaan met verstuurknop
- Typing indicator bij streaming ("..." animatie)
- Auto-scroll naar nieuw bericht

### Suggestie-chips
Klikbare voorbeeldvragen boven het tekstveld:

```
[Wat dekt een Budget pakket?] [Waarom is X duurder?] [Welke past bij mij?]
```

- Chips zijn configureerbaar via config.py
- Bij klikken: vult het tekstveld en stuurt automatisch
- Verdwijnen na eerste vraag (of blijven, te bepalen)

### Antwoord formatting
- AI antwoorden worden server-side gerenderd als HTML (markdown → HTML)
- Python `markdown` package voor conversie
- Ondersteunt: bold, lijstjes, tabelletjes
- Geen complexe markdown (geen code blocks, geen afbeeldingen)

---

## API Endpoints (stubs)

### POST /api/chat

```python
# web/routes/chat.py
@router.post("/chat")
async def chat(request: ChatRequest):
    # STUB: retourneert placeholder
    # Later: SSE stream via sse-starlette
    return {"message": "Chat is nog niet beschikbaar."}
```

**Request:**
```json
{
  "message": "Wat dekt een Budget pakket?",
  "history": [
    {"role": "user", "content": "Hallo"},
    {"role": "assistant", "content": "Hallo! Hoe kan ik helpen?"}
  ],
  "session_id": "abc123"
}
```

**Response (later, SSE stream):**
```
data: {"token": "Een"}
data: {"token": " Budget"}
data: {"token": " pakket"}
data: {"token": " dekt..."}
data: {"done": true}
```

### POST /api/chat/context

Koppelt vergelijkingsresultaten aan de chatsessie zodat de AI weet wat de klant heeft vergeleken.

```python
@router.post("/chat/context")
async def set_chat_context(session_id: str):
    # STUB: later ophalen van vergelijkingsresultaten
    # en meegeven aan LangGraph orchestrator
    return {"status": "context set"}
```

---

## Frontend (stub)

### partials/chat_section.html

```html
<section id="chat-section" class="chat-section">
  <h2>Stel een vraag</h2>
  
  <!-- Suggestie chips -->
  <div class="chat-chips">
    {% for chip in config.CHAT_SUGGESTIE_CHIPS %}
      <button class="chip">{{ chip }}</button>
    {% endfor %}
  </div>
  
  <!-- Berichten container -->
  <div id="chat-messages" class="chat-messages">
    <p class="chat-placeholder">Stel een vraag over de verzekeringen...</p>
  </div>
  
  <!-- Invoerveld -->
  <div class="chat-input">
    <input type="text" placeholder="Typ uw vraag..." disabled>
    <button disabled>Verstuur</button>
  </div>
  
  <p class="chat-notice">Chat wordt binnenkort beschikbaar.</p>
</section>
```

### partials/chat_message.html

```html
<div class="chat-bubble chat-bubble--{{ role }}">
  {{ content | safe }}
</div>
```

---

## Service (stub)

### web/services/chat_service.py

```python
class ChatService:
    """
    Stub voor chat service. Interface gedefinieerd, implementatie later.
    
    Later:
    - Koppeling met LangGraph orchestrator
    - Chat history management (sessie-gebaseerd)
    - Vergelijkingscontext meegeven
    - SSE streaming responses
    - Markdown → HTML conversie
    """
    
    async def send_message(
        self,
        message: str,
        history: list[dict],
        session_id: str
    ) -> str:
        # STUB
        return "Chat is nog niet beschikbaar."
    
    async def set_context(self, session_id: str, compare_results: dict):
        # STUB
        pass
```

---

## Koppeling met vergelijkingsresultaten

De chat moet weten wat de klant heeft vergeleken. Flow:

1. Klant doet vergelijking → krijgt `session_id`
2. Bij openen resultatenpagina: automatisch `POST /api/chat/context` met `session_id`
3. Backend koppelt de vergelijkingsresultaten aan de chatsessie
4. Als klant een vraag stelt, heeft de AI context over de vergelijking

---

## Toekomstige uitbreidingen blok

In `resultaten.html`:

```html
{% block extra_tools %}
  {# 
    Toekomstige componenten hier toevoegen.
    Elk component is een apart partial template.
    Voorbeeld:
    {% include "partials/callback_request.html" %}
    {% include "partials/document_download.html" %}
  #}
{% endblock %}
```

---

## Stappen

- [ ] chat_service.py — stub met interface
- [ ] POST /api/chat — stub endpoint
- [ ] POST /api/chat/context — stub endpoint
- [ ] partials/chat_section.html — placeholder UI
- [ ] partials/chat_message.html — bericht template
- [ ] Extra tools blok in resultaten.html
- [ ] Suggestie-chips in config.py
- [ ] Testen: chat sectie toont correct op resultatenpagina (disabled state)

---

## TODO: Exacte details nog toe te voegen

- [ ] Chat of vraagbalk (UX beslissing, architecturaal geen verschil)
- [ ] Exacte suggestie-chips teksten
- [ ] SSE streaming implementatie details
- [ ] LangGraph koppeling
- [ ] Chat history strategie (max N berichten, token limiet)
