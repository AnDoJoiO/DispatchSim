# Proyecto Dispatch

Simulador de emergencias 112 para formación de operadores. Un alertante IA (Claude) simula llamadas de emergencia; el operador practica la gestión en tiempo real con voz bidireccional.

**Stack:** FastAPI + SQLModel/Alembic + Vue 3 (Composition API, TypeScript) + Pinia + Vite + Tailwind CSS
**IA:** Anthropic Claude `claude-sonnet-4-6` (chat) · OpenAI Whisper (STT) · ElevenLabs/OpenAI (TTS)
**BD:** SQLite (dev) · PostgreSQL (prod/Railway)
**Deploy:** Railway vía Nixpacks + Procfile (uvicorn)
**Tests:** pytest (33 backend) + Vitest (21 frontend) · CI: GitHub Actions

---

## Próximo paso

**Auditoría profesional — Sesión 2:** aplicar los fixes de seguridad, UI y código pendientes de la auditoría (ver sección abajo).

---

## Auditoría de profesionalización (2026-03-21)

Sesión 1 completada — 7 fixes aplicados (password min 12, schema ScenarioCreate, 6 claves i18n, tokens legacy, dark mode landing, tipos utils.ts, Pydantic ConfigDict). 33/33 tests backend OK.

### Sesión 2 — Pendiente (seguridad + UI)

- [ ] Control de acceso en incidents: ownership check (operador solo ve/borra los suyos) — `app/api/v1/endpoints/incidents.py:61-93`
- [ ] Migrar inline `style=` → `<style scoped>` con CSS tokens — ScenarioEditor, DebriefingModal, EditUserModal, LoginModal
- [ ] Reemplazar colores hex hardcodeados → CSS tokens (`--success`, `--warning`, `--danger`) — ScenarioEditor
- [ ] Rate limit en silent trigger — `app/api/v1/endpoints/simulation.py:28-29`
- [ ] Responsive mobile: breakpoints en App.vue (sidebars colapsan en <768px) — `App.vue:67-87`

### Sesión 3 — Pendiente (robustez)

- [ ] Manejar `anthropic.RateLimitError` explícitamente — `app/services/ai_service.py:193-211`
- [ ] Fix race condition en silent trigger (row-level locking) — `simulation.py:37-43`
- [ ] Fix memory leak graceTimer en useAudioController — `useAudioController.ts:39`
- [ ] Mejorar CSP: quitar `'unsafe-inline'` de script-src — `app/main.py:30`
- [ ] Prevenir múltiples reloads simultáneos en 401 — `frontend/src/api/index.ts:16`
- [ ] Añadir HSTS header para producción — `app/main.py:44-47`

### Pendiente menor (medium)

- [ ] Timeout en queries SQLite — `app/db/session.py`
- [ ] Eliminar `console.error` en producción — `useTTS.ts:35,41`
- [ ] Validar param `lang` en ChatRequest — `simulation.py:9`
- [ ] Try-except en timeout APIs externas — `voice.py:147-154`
- [ ] Actualizar pip a >=26.0 (CVE-2025-8869, CVE-2026-1703)

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

## Tareas pendientes

### [ ] Integración ElevenLabs TTS emocional
- Modelo: `eleven_turbo_v2_5`
- Reemplaza el TTS actual con soporte de voces emocionales
- Prompt guardado en: [PENDIENTE - preguntar a Agustín dónde lo guardó]
- Requisitos previos: `ELEVENLABS_API_KEY` (plan Starter $5/mes en elevenlabs.io)
- Impacto: alta mejora perceptible en realismo del simulador

### [ ] Dashboard de analíticas por operador
- Panel para formadores con KPIs por operador: nº simulaciones, puntuación media, evolución temporal
- Comparativa entre operadores del mismo equipo
- Exportación de informes (PDF o CSV)
- Referencia competidora: Sklls, AnthroPi

### [ ] Replay de audio por simulación
- Permitir al formador escuchar el audio completo de una simulación pasada
- Sincronizado con la transcripción [OPR]/[ALT] en pantalla
- Almacenamiento de audios en Railway / S3 con retención configurable
- Referencia competidora: AnthroPi (su principal diferencial de debriefing)

### [ ] Mapa de localización de llamada
- Durante la simulación, mostrar un mapa con el punto de origen de la llamada (coordenadas generadas por la IA coherentes con la zona del cliente)
- Simular la experiencia real de localización automática que tienen los CAD (Computer Aided Dispatch) reales
- El punto aparece progresivamente (simular latencia de localización real, no inmediata)
- Posible indicador de confianza de localización (GPS fijo / triangulación aproximada / no localizado)
- Stack sugerido: Leaflet.js + OpenStreetMap (gratuito, sin límites de API)
- Referencia: sistema CAD real de Bombers d'Andorra (localización automática de llamadas entrantes)
- Aportación diferencial: ningún competidor actual (Sklls, ThisGen, AnthroPi) tiene esta feature documentada

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

## Protocolo de Auditoría

### Cuándo ejecutarla
Antes de cualquier merge a main con cambios significativos (nueva feature, refactor, fix de seguridad, rediseño UI).

### Orden de verificación
```bash
# 1. Tests backend
cd /home/agu/Proyecto_Dispatch && python -m pytest tests/ -v

# 2. Tests frontend
cd frontend && npx vitest run

# 3. Deps backend (requiere pip-audit: pip install pip-audit)
pip audit

# 4. Deps frontend
npm audit
```

### Criterios de bloqueo
- **Critical / High:** bloquean el commit — se resuelven antes de pushear
- **Medium:** se resuelven en la misma sesión de trabajo
- **Low:** se acumulan en el roadmap (backlog)

### Checks de coherencia post-rediseño
- Tokens CSS sincronizados `landing.html :root` ↔ `main.css :root` (mateixos valors)
- i18n completo en els 4 idiomes (CA/ES/FR/EN) — verificar claus noves
- No usar tokens legacy en codi nou: usar `--text-muted` (no `--text3`), `--text-secondary` (no `--text2`), `--surface-raised` (no `--surface2`)
- Inline `style=` prohibit en components nous — usar scoped CSS amb tokens semàntics

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
