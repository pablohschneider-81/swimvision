# F4F Assistant — Agente de WhatsApp de Fittest4Fit

Agente de WhatsApp con IA para **Fittest4Fit (Hernán Schneider)**, generado
con el enfoque de [AgentKit](https://github.com/Hainrixz/whatsapp-agentkit).

## Qué hace

- Responde preguntas frecuentes sobre los programas (NeuroForce, La Fórmula
  21 Días, Mentoría Fluidez, entrenamiento de fuerza para nadadores).
- Detecta leads interesados y los deja registrados para seguimiento comercial.
- Junta los datos para coordinar una mentoría/consulta con Hernán (la
  confirmación final del turno sigue siendo manual — no hay calendario
  conectado todavía).
- Tono: vendedor y persuasivo, pero siempre resolviendo primero.

## Estructura

```
agent/
├── main.py            Servidor FastAPI + webhook de WhatsApp
├── brain.py            Conexión con Claude API (el cerebro)
├── memory.py            Historial de conversación + leads + solicitudes de mentoría (SQLite)
├── tools.py            Herramientas de negocio (leads, mentorías, búsqueda en /knowledge)
└── providers/
    ├── base.py          Interfaz común
    ├── __init__.py      Selecciona el proveedor según .env
    └── twilio.py         Adaptador de Twilio (proveedor elegido)

config/
├── business.yaml        Datos del negocio
└── prompts.yaml          System prompt del agente

knowledge/
└── programas-f4f.md      Resumen de los programas (editable — sumar precios/cupos reales)

tests/
└── test_local.py         Chat de prueba en terminal, sin WhatsApp
```

## Cómo probarlo localmente

1. Copiá `.env.example` a `.env` y completá:
   - `ANTHROPIC_API_KEY` (https://platform.anthropic.com/settings/api-keys)
   - `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`
     (sandbox gratis en https://twilio.com → Messaging → Try it Out →
     Send a WhatsApp message)

   **Nunca pegues tus API keys reales en un chat o en el repo** — solo van
   en tu `.env` local, que ya está en `.gitignore`.

2. Instalá dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Chat de prueba sin WhatsApp:
   ```bash
   python tests/test_local.py
   ```

4. Servidor real (para conectar el webhook de Twilio):
   ```bash
   uvicorn agent.main:app --reload --port 8000
   ```

## Deploy a producción (Railway)

1. `docker compose build` para verificar que la imagen levanta bien.
2. Subís el repo a GitHub (ya lo estás usando) y conectás Railway al repo.
3. En Railway → Variables, cargás las mismas variables del `.env`
   (`ANTHROPIC_API_KEY`, `WHATSAPP_PROVIDER=twilio`,
   `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`,
   `PORT`, `ENVIRONMENT=production`, y `DATABASE_URL` de Postgres si
   agregás esa base).
4. En Twilio Console → Messaging → WhatsApp Sandbox Settings, poné como
   webhook: `https://tu-app.up.railway.app/webhook` (método POST).

## Pendiente / próximos pasos sugeridos

- Sumar precios y cupos reales a `knowledge/programas-f4f.md`.
- Conectar `solicitar_mentoria()` (en `agent/tools.py`) a un calendario real
  (por ejemplo Calendly) en vez de dejarlo como cola manual.
- Si querés que el agente ejecute estas herramientas automáticamente durante
  la conversación (en vez de solo tener las funciones listas), hay que
  agregar tool-calling a `agent/brain.py` con la API de Claude.
