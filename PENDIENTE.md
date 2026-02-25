# PENDIENTE — Mejoras y correcciones del proyecto
> Actualizar este archivo cada vez que se complete un punto.
> Orden: de mayor a menor importancia.

---

## 🔴 CRÍTICO (seguridad / integridad de datos)

- [x] **Bug bcrypt `verify_password`** — `encode()`/`decode()` sin charset explícito y sin guard de tipo.
  _Arreglado en `app/core/security.py`: UTF-8 explícito + `isinstance` guard._

- [x] **`SECRET_KEY` por defecto insegura** — `config.py` tiene `"change-me-in-production"` como valor por defecto.
  _Arreglado en `app/core/config.py`: `@model_validator` bloquea el arranque si `DEBUG=False` y la clave es la de por defecto o tiene menos de 32 caracteres._

- [x] **Sin protección CSRF** — Todas las peticiones de estado (POST/PATCH/DELETE) se hacen sin token CSRF.
  _El app usa Bearer tokens en `localStorage` (no cookies), por lo que el CSRF clásico no aplica. Protección implementada mediante `CORSMiddleware` en `app/main.py` con lista de orígenes permitidos configurable vía `ALLOWED_ORIGINS` en `.env`. Cualquier origen no listado recibe 403 en preflight._

- [x] **Authorization bypass en escenarios** — Cualquier usuario con rol FORMADOR puede borrar escenarios que no creó.
  _Decisión del usuario: comportamiento correcto, cualquier formador puede gestionar cualquier escenario. No requiere cambio._

---

## 🟠 URGENTE (calidad y robustez)

- [x] **Sin rate limiting** — El endpoint `/simulate/chat` llama a la API de Anthropic sin límite de frecuencia.
  _Arreglado con `SlidingWindowLimiter` en `app/core/rate_limit.py` (sin dependencias externas). Límite: 10 mensajes/minuto por usuario autenticado. Devuelve HTTP 429 si se supera._

- [x] **Errores de IA exponen detalle interno** — `detail=f"Error de la IA: {exc}"` envía el mensaje raw al cliente.
  _Arreglado: `logger.exception(...)` en servidor, mensaje genérico al cliente. Además el missatge de l'operador es persisteix abans de cridar la IA._

- [x] **Sin logging de eventos de seguridad** — No se registran logins fallidos, accesos denegados ni borrados masivos.
  _Arreglado: `logger.warning(...)` en `auth.py` (LOGIN_FAILED, LOGIN_DENIED_INACTIVE, LOGIN_DENIED_EXPIRED) i `deps.py` (AUTH_INVALID_TOKEN, AUTH_DENIED_INACTIVE, AUTH_DENIED_EXPIRED, ACCESS_DENIED)._

- [ ] **Sin validación de formato en `username`** — Permite caracteres especiales y unicode.
  Añadir `pattern=r'^[a-zA-Z0-9_]{3,50}$'` en `UserCreate`.
  _Archivo: `app/schemas/user.py`_

- [ ] **`instructions_ia` sin longitud máxima** — Podría enviarse un texto enorme a la IA, causando coste/DoS.
  Añadir `max_length=2000` en el schema.
  _Archivo: `app/schemas/scenario.py`_

- [x] **Mensaje del operador no se persiste si la IA falla** — resolt conjuntament amb el punt anterior.

---

## 🟡 IMPORTANTE (mantenibilidad y consistencia)

- [ ] **Migraciones con Alembic** — Actualmente se usa `PRAGMA table_info` SQLite-only para migraciones manuales.
  Reemplazar por Alembic para compatibilidad y trazabilidad.
  _Archivo: `app/db/session.py:8-14`_

- [ ] **Inconsistencia de idioma en mensajes de error HTTP** — Mezcla de español y catalán.
  Unificar todo en catalán.
  Ejemplos: `"Incidencia no encontrada"` vs `"Incidència no trobada"`.
  _Archivos: `app/api/v1/endpoints/incidents.py` (varias líneas)_

- [ ] **Sin paginación en historial ni usuarios** — `list_history` y `list_users` devuelven todos los registros.
  Añadir parámetros `skip`/`limit`.
  _Archivos: `app/api/v1/endpoints/history.py`, `app/api/v1/endpoints/users.py`_

- [ ] **N+1 query en historial** — El conteo de mensajes se hace en Python iterando todos los `ChatMessage`.
  Usar `func.count()` con `GROUP BY` en la query SQL.
  _Archivo: `app/api/v1/endpoints/history.py:50-54`_

- [ ] **Sin índices en claves foráneas** — `creator_id`, `operator_id`, `scenario_id` en `Incident` no tienen índice explícito.
  Añadir `index=True` en los Fields correspondientes.
  _Archivo: `app/models/incident.py:24-26`_

- [ ] **Valores hardcoded fuera de config** — `CLEANUP_INTERVAL_SECONDS=3600`, `max_tokens=512` están en el código.
  Mover a `app/core/config.py`.
  _Archivos: `app/services/cleanup.py:15`, `app/services/ai_service.py:36`_

- [ ] **Mezcla de idiomas en el código fuente** — Variables en español (`instructions_ia`), comentarios en inglés, errores en catalán.
  Decidir un idioma para el código (recomendado: inglés) y unificar progresivamente.

---

## 🟢 MEJORA (calidad de código)

- [x] **Frontend monolítico** — `index.html` tiene 1.300+ líneas mezclando HTML, CSS y JS.
  _Migrat a Vue 3 + Vite + Pinia + Tailwind CSS (npm). 11 components, 6 stores, capa API separada. Build genera `app/static/index.html` + `app/static/assets/`. `landing.html` preservada._

- [x] **Estado global sin estructura en JS** — 13+ variables globales sueltas.
  _Resolt amb la migració a Vue 3 + Pinia. Cada store (auth, app, emergency, history, users, ui) gestiona el seu propi estat de forma reactiva._

- [ ] **Sin tests** — Cero cobertura de tests unitarios o de integración.
  Prioridad mínima: tests para `security.py`, `deps.py`, endpoints de auth y borrado en cascada.

- [x] **Headers de seguridad HTTP ausentes** — No hay `Content-Security-Policy`, `X-Frame-Options`, `X-Content-Type-Options`.
  _Arreglado con `SecurityHeadersMiddleware` en `app/main.py`: añade `X-Content-Type-Options`, `X-Frame-Options: DENY`, `Referrer-Policy` y `Content-Security-Policy` en todas las respuestas._

- [ ] **Sin configuración CORS explícita** — No hay `CORSMiddleware` en `main.py`.
  Añadir aunque sea restrictivo por defecto.

- [ ] **`additional_risks` como CSV en BD** — Campo de texto plano `"Gas,Electricitat,Químics"`.
  Considerar tabla de relación o campo JSON para mayor integridad.
  _Archivo: `app/models/intervention.py:16`_

- [ ] **Abreviaciones inconsistentes en el código** — `inc`/`incident`, `sc`/`scenario`, `msg`/`message` mezclados.
  Unificar en los nuevos desarrollos.

---

## ✅ COMPLETADO

- [x] Añadir campo `expires_at` a usuarios operadores (modelo, migración, schemas, API, frontend)
- [x] Endpoint `PATCH /users/{id}` para editar `is_active` y `expires_at`
- [x] Bloqueo de login y API calls para usuarios caducados (auth + deps)
- [x] UI: campo de caducidad en creación, columna en tabla, modal de edición
- [x] Endpoints `DELETE /history/{id}` y `DELETE /history` (individual, batch, todo)
- [x] UI: toolbar de selección múltiple y borrado en historial
- [x] Servicio de limpieza automática de usuarios expirados con borrado en cascada
- [x] Loop de background en lifespan (ejecuta cada hora)
- [x] Fix `verify_password`: UTF-8 explícito + guard `isinstance`
- [x] Fix cliente Anthropic: instanciación por llamada en vez de al importar módulo
- [x] Prompt de la IA: reglas estrictas para evitar respuestas anticipadas y acotaciones

---

_Última actualización: 2026-02-25 — Migració Vue 3 completada_
