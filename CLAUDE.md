# Proyecto Dispatch

Simulador de emergencias 112 para formación de operadores. Un alertante IA (Claude) simula llamadas de emergencia; el operador practica la gestión en tiempo real con voz bidireccional.

**Stack:** FastAPI + SQLModel/Alembic + Vue 3 (Composition API) + Pinia + Vite + Tailwind CSS
**IA:** Anthropic Claude (chat) · OpenAI Whisper (STT) · ElevenLabs/OpenAI (TTS)
**BD:** SQLite (dev) · PostgreSQL (prod/Railway)
**Deploy:** Railway vía Procfile (uvicorn)

---

## Roadmap de refactorización

### Fase 1 — Estabilidad y seguridad

- [x] Rate limit en `/voice/transcribe` y `/voice/speak` — 15 req/min por usuario
- [x] Rate limit en `/auth/login` — 5 intentos/min por username
- [x] Validar `silent_trigger` server-side — 409 si el último mensaje no es del assistant
- [x] Usar `EL_TO_OAI_VOICE` de `constants.py` en `voice.py` — eliminado dict duplicado
- [x] Fix transacción en `simulation_service.py` — user+assistant se persisten atómicamente en un solo commit
- [x] Añadir `ondelete="CASCADE"` en FKs — migración `7053c17081fa` (CASCADE en chatmessage/interventiondata, SET NULL en creator/operator/scenario)
- [x] Límite de tamaño en audio upload — 5 MB máximo en `/voice/transcribe`

### Fase 2 — Calidad de código

- [x] Paginación en `GET /incidents` y `GET /scenarios` — skip/limit (default 0/100, max 500)
- [x] Centralizar error handling en frontend — `apiFetch` lanza `ApiError`, devuelve JSON directamente
- [x] Eliminar prop drilling en ChatWindow — de 13 props a 4 (solo mic*), usa stores directamente
- [x] Dependencia circular chat↔call — mantenida con lazy imports (patrón Pinia estándar, funciona correctamente)
- [x] Centralizar magic numbers en `frontend/src/config.js` — VAD, timers, thresholds
- [x] Validación de formularios en FitxaPanel (address requerido) y ScenarioEditor (ya tenía)
- [x] Estandarizar patrón de errores en stores — todos usan try/catch con ApiError

### Fase 3 — Testing

- [x] Setup pytest + fixtures (conftest.py, test DB SQLite, auto-reset rate limiters)
- [x] Tests unitarios: security.py (hash, verify, JWT create/decode/expired/tampered), rate_limit.py (sliding window, 429, expiry, independent keys)
- [x] Tests de integración: auth (register, login, duplicates, inactive/expired, rate limit, me), incidents (CRUD, pagination, end call, 409 double-end), cascade delete (incident → chatmessage + interventiondata)
- [x] Tests frontend (Vitest 1.6): api wrapper (7 tests), auth+app stores (9 tests), config (5 tests)

### Fase 4 — Infraestructura

- [x] GitHub Actions CI — backend (pytest) + frontend (vitest + build) en push/PR a main
- [x] Dockerfile multi-stage — Node 20 (build frontend) + Python 3.12-slim (runtime)
- [x] GZipMiddleware en FastAPI (min 500 bytes)
- [x] Structured logging — JSON en producció, text llegible en dev

### Fase 5 — Mejoras opcionales

- [ ] Migrar frontend a TypeScript
- [ ] Accesibilidad: aria-labels, for/id en labels, keyboard nav
- [ ] Cache-Control headers para assets con hash
- [ ] Eliminar `websockets` de requirements.txt (no se usa)
- [ ] `additional_risks` como JSON en BD en vez de CSV

---

## Estado actual

Tareas completadas en iteraciones anteriores:

- [x] Auth JWT + bcrypt + roles (admin/formador/operador) + expiración de cuentas
- [x] SecurityHeadersMiddleware (CSP, X-Frame-Options, nosniff, Referrer-Policy)
- [x] CORS configurable con ALLOWED_ORIGINS
- [x] Rate limit chat: SlidingWindowLimiter 10 msg/min por usuario
- [x] Validación de inputs: username regex, operator_message 1000 chars, instructions_ia 2000 chars
- [x] Logging de seguridad: LOGIN_FAILED, AUTH_INVALID_TOKEN, ACCESS_DENIED, etc.
- [x] Errores IA: logger.exception server-side, mensaje genérico al cliente
- [x] Migraciones Alembic + índices en FKs
- [x] Paginación en GET /history y GET /users
- [x] Cleanup automático de usuarios expirados (asyncio loop cada hora)
- [x] Frontend migrado a Vue 3 + Vite + Pinia + Tailwind CSS (8 stores)
- [x] i18n completo CA/ES/FR/EN con selector en landing
- [x] Voz bidireccional: STT (Whisper + VAD) + TTS (ElevenLabs → OpenAI fallback)
- [x] IA responde en idioma de la web; instructions_ia del formador pueden sobreescribirlo
- [x] Reacción de la IA al silencio del operador (hasta 3 veces)
- [x] N+1 query en historial resuelto con GROUP BY

### QA pendiente (producción/Railway)

- [ ] Flujo operador: login → escenario → incidente → chat IA (cada idioma) → finalizar → ficha → debriefing
- [ ] Flujo formador: crear escenario → crear operador con caducidad → historial → borrar
- [ ] Flujo admin: crear formador → editar usuario → verificar caducidad en login

---

## Contexto técnico

### Arquitectura backend
- **Entrada:** `app/main.py` — lifespan crea BD, seed admin, arranca cleanup
- **Rutas:** `app/api/v1/router.py` agrupa 8 routers (auth, users, scenarios, incidents, simulation, voice, interventions, history)
- **Modelos:** SQLModel en `app/models/` — User, Incident, ChatMessage, InterventionData, Scenario
- **Servicios:** `ai_service.py` (prompt Claude), `simulation_service.py` (orquesta un turno de chat), `cleanup.py` (expira usuarios)
- **Config:** Pydantic Settings en `app/core/config.py`, validación de SECRET_KEY en producción

### Arquitectura frontend
- **Entry:** `frontend/src/main.js` → `App.vue` (no hay Vue Router, navegación por tabs via Pinia `app.activeTab`)
- **Stores Pinia (8):** auth, app, call, chat, scenarios, ui, history, users
- **Composables:** useAudioController (silence detection), useMicrophone (VAD + Whisper), useTTS (ElevenLabs/OpenAI)
- **Build:** Vite con `base: '/static/'`, output a `app/static/`, `emptyOutDir: false` para preservar landing.html
- **API client:** `frontend/src/api/index.js` — fetch wrapper con Bearer token, auto-logout en 401

### Decisiones de diseño
- **Sin WebSockets:** chat es request-response HTTP; suficiente para simulación 1:1
- **Sin Vue Router:** app de pestaña única; tabs gestionados con Pinia
- **Idioma de la IA:** regla imperativa en system prompt; `instructions_ia` del formador puede sobreescribirlo
- **`instructions_ia` es secreto:** no se devuelve en ScenarioRead (solo en BD para el system prompt)
- **Voz emocional:** 3 voces ElevenLabs mapeadas a InitialEmotion del escenario (Calma→Sarah, Pánico→Jessica, Agresión→Adam)
- **Silent trigger:** frontend detecta 9s de silencio, envía `silent_trigger=true`; backend guarda `[silenci]` como mensaje user para mantener alternancia user/assistant requerida por la API de Anthropic
- **Cascade delete manual:** history.py borra ChatMessages + InterventionData antes del Incident (sin CASCADE en BD)
