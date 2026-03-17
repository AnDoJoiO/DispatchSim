# Proyecto Dispatch

Simulador de emergencias 112 para formación de operadores. Un alertante IA (Claude) simula llamadas de emergencia; el operador practica la gestión en tiempo real con voz bidireccional.

**Stack:** FastAPI + SQLModel/Alembic + Vue 3 (Composition API, TypeScript) + Pinia + Vite + Tailwind CSS
**IA:** Anthropic Claude `claude-sonnet-4-6` (chat) · OpenAI Whisper (STT) · ElevenLabs/OpenAI (TTS)
**BD:** SQLite (dev) · PostgreSQL (prod/Railway)
**Deploy:** Railway vía Nixpacks + Procfile (uvicorn)
**Tests:** pytest (33 backend) + Vitest (21 frontend) · CI: GitHub Actions

---

## Próximo paso

**Fase 6.1 — Filtro alucinaciones STT:** validar transcripción en backend antes de enviar a Claude (texto muy corto, solo símbolos, sin palabras reales) + instrucción en system prompt del operador.

---

## Roadmap pendiente

### Fase 6 — Bugs de producción

- [ ] Filtro alucinaciones STT: validar transcripción en backend antes de enviar a Claude (texto muy corto, solo símbolos, sin palabras reales) + instrucción en system prompt del operador
- [ ] Tool Use: que la IA rellene automáticamente la ficha del incidente durante la simulación
- [ ] Mejorar system prompt del operador 112: más robusto ante situaciones confusas

### Fase 7 — Seguridad y resiliencia

- [ ] Secrets scanning del historial git
- [ ] Dependency audit (npm audit + pip audit)
- [ ] Configurar backups automáticos de BD en Railway

---

## Historial completado

<details>
<summary>Fases 1-5 completadas (26 tareas) — click para expandir</summary>

- **Fase 1 — Estabilidad y seguridad:** Rate limits (voice, login), validación silent_trigger, dict duplicado eliminado, transacción atómica, CASCADE en FKs (migración 7053c17081fa), límite 5MB audio upload
- **Fase 2 — Calidad de código:** Paginación incidents/scenarios, ApiError centralizado, ChatWindow sin prop drilling (13→4 props), config.ts con magic numbers, validación formularios, errores estandarizados en stores
- **Fase 3 — Testing:** pytest + fixtures + 33 tests backend (security, rate limit, auth, incidents, cascade delete) + Vitest + 21 tests frontend (api, stores, config)
- **Fase 4 — Infraestructura:** GitHub Actions CI, Dockerfile multi-stage, GZipMiddleware, structured logging JSON/text
- **Fase 5 — Mejoras opcionales:** TypeScript completo (types.ts + stores + composables + .vue lang=ts), accesibilidad (for/id, aria-labels, autocomplete), Cache-Control headers, websockets eliminado

**Trabajo anterior a las fases:**
Auth JWT + bcrypt + roles, SecurityHeadersMiddleware, CORS, rate limit chat, validación inputs, logging seguridad, Alembic + índices FK, paginación history/users, cleanup usuarios expirados, Vue 3 + Vite + Pinia + Tailwind, i18n CA/ES/FR/EN, voz bidireccional STT+TTS, reacción IA al silencio, N+1 query historial, auto-fin trucada amb [FI]

</details>

---

## Contexto técnico

### Arquitectura backend
- **Entrada:** `app/main.py` — lifespan crea BD, seed admin, arranca cleanup, setup logging
- **Rutas:** `app/api/v1/router.py` agrupa 8 routers (auth, users, scenarios, incidents, simulation, voice, interventions, history)
- **Modelos:** SQLModel en `app/models/` — User, Incident, ChatMessage, InterventionData, Scenario
- **Servicios:** `ai_service.py` (prompt Claude), `simulation_service.py` (orquesta un turno de chat + detecció [FI]), `cleanup.py` (expira usuarios)
- **Config:** Pydantic Settings en `app/core/config.py`, validación de SECRET_KEY en producción
- **BD:** `PRAGMA foreign_keys=ON` per SQLite, `passive_deletes="all"` en relationships, CASCADE/SET NULL en FKs

### Arquitectura frontend
- **Entry:** `frontend/src/main.ts` → `App.vue` (no hay Vue Router, navegación por tabs via Pinia `app.activeTab`)
- **Stores Pinia (8):** auth, app, call, chat, scenarios, ui, history, users — todos tipats amb `Ref<T>`
- **Composables:** useAudioController (silence detection + mic lifecycle), useMicrophone (VAD + Whisper), useTTS (AudioContext + BufferSource)
- **Types:** `frontend/src/types.ts` — 13 interfaces (User, Scenario, Incident, ChatMessage, ChatResponse, etc.)
- **Build:** Vite + TypeScript, `base: '/static/'`, output a `app/static/`
- **API client:** `frontend/src/api/index.ts` — `apiFetch<T>` amb genèrics, llança `ApiError`, auto-logout en 401

### Decisiones de diseño
- **Sin WebSockets:** chat es request-response HTTP; suficiente para simulación 1:1
- **Sin Vue Router:** app de pestaña única; tabs gestionados con Pinia
- **Idioma de la IA:** regla imperativa en system prompt; `instructions_ia` del formador puede sobreescribirlo
- **`instructions_ia` es secreto:** no se devuelve en ScenarioRead (solo en BD para el system prompt)
- **Voz emocional:** 3 voces ElevenLabs mapeadas a InitialEmotion del escenario (Calma→Sarah, Pánico→Jessica, Agresión→Adam)
- **Silent trigger:** frontend detecta 15s de silencio, envía `silent_trigger=true`; backend valida que el último mensaje sea del assistant; guarda `[silenci]` para mantener alternancia user/assistant
- **Auto-fi trucada:** IA genera `[FI]` al final del missatge quan l'operador tanca la trucada; backend el detecta, finalitza l'incident, i retorna `call_ended: true`; frontend demora `_onAutoEnd` 100ms perquè el TTS s'iniciï abans del `stopTTS`
- **TTS amb AudioContext:** substitueix `new Audio()` per evitar bloqueig d'autoplay del navegador; es desbloqueja amb el primer clic/tecla
- **Micro suspès durant IA:** el micro es suspèn quan l'operador envia missatge i no es reactiva fins que el TTS acaba + 600ms delay; `_discardNext` flag evita processar àudio capturat durant el TTS
