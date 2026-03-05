# PENDIENTE — Mejoras y correcciones del proyecto
> Actualizar este archivo cada vez que se complete un punto.
> Orden: de mayor a menor importancia.

---

## 🔴 CRÍTICO (seguridad / integridad de datos)

- [x] **Bug bcrypt `verify_password`** — UTF-8 explícito + guard `isinstance`. `app/core/security.py`
- [x] **`SECRET_KEY` por defecto insegura** — `@model_validator` bloquea arranque si es insegura. `app/core/config.py`
- [x] **Sin protección CSRF** — Resuelto: JWT en header + `CORSMiddleware` con `ALLOWED_ORIGINS`. `app/main.py`
- [x] **Authorization bypass escenarios** — Decisión: cualquier formador gestiona cualquier escenario. OK.

---

## 🟠 URGENTE (calidad y robustez)

- [x] **Sin rate limiting en `/simulate/chat`** — `SlidingWindowLimiter` 10 msg/min por usuario. `app/core/rate_limit.py`
- [x] **Errores IA exponen detalle interno** — `logger.exception` en servidor, mensaje genérico al cliente.
- [x] **Sin logging de seguridad** — LOGIN_FAILED, AUTH_INVALID_TOKEN, ACCESS_DENIED, etc.
- [x] **Mensaje operador no se persistía si la IA fallaba** — Se persiste antes de llamar a la IA.

- [x] **Sin validación de formato en `username`** — `pattern=r'^[a-zA-Z0-9_]+$'` añadido. `app/schemas/user.py`
- [x] **Sin límite de longitud en `operator_message`** — `max_length=1000` añadido. `app/schemas/simulation.py`
- [x] **Sin límite de longitud en `instructions_ia`** — `max_length=2000` añadido. `app/schemas/scenario.py`

---

## 🟡 IMPORTANTE (mantenibilidad)

- [x] **N+1 query en historial** — Resuelto con `func.count() GROUP BY`. `app/api/v1/endpoints/history.py`

- [x] **Migraciones con Alembic** — `alembic/` inicializado con baseline `1778e8263c1c`. `session.py` usa `create_all + stamp` en primera ejecución y `upgrade head` en las siguientes. `alembic revision --autogenerate` para futuros cambios.

- [x] **Sin paginación en historial ni usuarios** — `skip`/`limit` (default 0/100, max 500) añadidos a `GET /history` y `GET /users`. Backward compatible con frontend.

- [x] **Inconsistencia de idioma en errores HTTP** — 3 mensajes en español en `incidents.py` corregidos a catalán ("Incidència no trobada").

- [x] **Sin índices en claves foráneas** — `index=True` añadido a todas las FK: `creator_id`/`operator_id`/`scenario_id` (incident), `incident_id` (chatmessage, interventiondata), `creator_id` (scenario). Migración `02c688e14b2b` aplicada.

- [x] **Valores hardcoded fuera de config** — `CLEANUP_INTERVAL_SECONDS` y `AI_MAX_TOKENS` movidos a `config.py`. Configurables vía `.env`.

---

## 🟢 MEJORA (calidad de código)

- [x] **Frontend monolítico** — Migrado a Vue 3 + Vite + Pinia + Tailwind CSS.
- [x] **Estado global sin estructura** — Resuelto con 6 Pinia stores.
- [x] **9 bugs Vue post-migración** — Todos corregidos (reactivity, fmtDuration, isExpired, IDs, etc.)
- [x] **Headers de seguridad HTTP ausentes** — `SecurityHeadersMiddleware` añadido. `app/main.py`
- [x] **Sin CORS explícito** — `CORSMiddleware` con `ALLOWED_ORIGINS` configurable.

- [ ] **Sin tests** — Cero cobertura. Prioridad mínima: `security.py`, auth endpoints, borrado en cascada.

- [ ] **Sin rate limiting en endpoints de voz** — `/voice/transcribe` y `/voice/speak` sin límite. Riesgo de costes masivos en OpenAI/ElevenLabs si se abusa. Aplicar el mismo `SlidingWindowLimiter` que en `/simulate/chat`. `app/api/v1/endpoints/voice.py`

- [ ] **Sin límite de tamaño en audio upload** — `/voice/transcribe` acepta archivos de cualquier tamaño. Añadir validación de `content_length` o tamaño máximo del blob. `app/api/v1/endpoints/voice.py`

- [ ] **`additional_risks` como CSV en BD** — Texto plano `"Gas,Electricitat,Químics"`.
  Considerar tabla de relación o campo JSON.
  _Archivo: `app/models/intervention.py`_

---

## 🔜 PRÓXIMA SESIÓN — Por dónde continuar

### ~~Paso 1 — Protección de costes~~ ✅ COMPLETADO

### Paso 2 — QA manual de flujos completos
Probar los 3 flujos de cabo a rabo en producción (Railway):
- [ ] **Operador**: login → seleccionar escenario → iniciar incidente → chat IA (en cada idioma) → finalizar llamada → rellenar ficha → guardar → debriefing
- [ ] **Formador**: crear escenario → crear operador con caducidad → historial → borrar historial
- [ ] **Admin**: crear formador → editar usuario → verificar caducidad en login

### ~~Paso 3 — Voz~~ ✅ COMPLETADO
- [x] **Speech-to-text** operador — MediaRecorder + VAD automático + OpenAI Whisper. Auto-envío al silencio (800ms). Filtro anti-alucinaciones.
- [x] **Text-to-speech** alertante — ElevenLabs `eleven_multilingual_v2` (fallback OpenAI TTS). Voz según emoción del escenario (Sarah/Jessica/Adam). Frases en paralelo para inicio rápido. Micro pausado durante TTS.

---

## ✅ COMPLETADO (historial)

- [x] Campo `expires_at` para operadores (modelo, migración, schemas, API, frontend)
- [x] Endpoint `PATCH /users/{id}` para editar estado y caducidad
- [x] Bloqueo de login y API calls para usuarios caducados
- [x] Endpoints `DELETE /history/{id}`, batch y total
- [x] UI toolbar de selección múltiple y borrado en historial
- [x] Servicio de limpieza automática de usuarios expirados (loop asyncio cada hora)
- [x] Prompt IA: reglas estrictas (sin anticipar, sin acotaciones, respuestas cortas)
- [x] Migración frontend a Vue 3 + Vite + Pinia + Tailwind CSS
- [x] Separación gestión (escenarios/usuarios) del simulador — layout independiente en `App.vue`
- [x] Refactorización schema escenario: `location_exact`, `victim_status` (Enum), `initial_emotion` (Enum)
- [x] Migración BD (SQLite + PostgreSQL) para nuevos campos de escenario
- [x] `ScenarioEditor.vue` — componente dedicado con layout master-detail
- [x] IA usa campos estructurados del escenario en el system prompt
- [x] N+1 query historial → `func.count() GROUP BY`
- [x] i18n completo CA/ES/FR/EN — simulador, formularios y componentes de gestión
- [x] Selector de idioma en landing → sincronizado con toda la app Vue
- [x] **IA responde en el idioma seleccionado en la web** — regla estricta e imperativa en system prompt; niega hablar otros idiomas; las `instructions_ia` del formador pueden sobreescribirlo

---

_Última actualización: 2026-03-04 — Voz bidireccional completa (STT + TTS). Pendiente: QA manual en producción._
