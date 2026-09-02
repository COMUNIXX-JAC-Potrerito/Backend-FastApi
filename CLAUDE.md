# CONTEXTO COMPLETO — COMUNIX Backend

Documento de contexto para que cualquier IA (o persona) retome el trabajo sin perder nada. Leer completo antes de responder. Si algo aquí contradice lo que el usuario (Juanca) dice en el momento, gana lo que él diga ahora — esto es un resumen, no la fuente de verdad definitiva.

---

## 1. QUÉ ES COMUNIX

Sistema de gestión comunitaria para la Junta de Acción Comunal (JAC) de la **Vereda Potrerito**. Es el **proyecto integrador (capstone)** del programa Análisis y Desarrollo de Software (ADSO) del SENA.
- Deadline: **1 de septiembre de 2026**, dividido en **8 sprints** de dos semanas.
- Instructor: **Efrén Moreno Valoyes**.
- 5 épicas: (1) Gestión/Administración/Seguimiento por la JAC, (2) Interacción de la Comunidad y Radicación de PQRS, (3) Divulgación de Información y Actividades, (4) Comunicación y Gestión Documental, (5) Participación Comunitaria y Notificaciones.
- 21 historias de usuario con priorización MoSCoW.
- 4 roles: Usuario, Administrador, Superadministrador, Entidad.
- Requerimientos: RF01–RF14 funcionales, RNF01–RNF08 no funcionales.

---

## 2. ARQUITECTURA Y STACK (actualizado — antes era React+Node+MySQL, YA NO)

Arquitectura **desacoplada**, dos repos de GitHub en una organización:
- **Backend**: Python + gestor `uv` + **FastAPI** + **PostgreSQL**. Repo: https://github.com/COMUNIXX-JAC-Potrerito/Backend-FastApi.git — carpeta local `C:\Sena 2026\Desarrollo Comunix\COMUNIXX`.
- **Frontend**: JavaScript con **Angular**. Aún NO empezado (a cargo de David).
- **Despliegue previsto del backend**: Render, plan gratuito.

---

## 3. EQUIPO Y ROLES

- **Juan Camilo Montes (Juanca / "yo")** — estructura y funcionalidades del backend: modelos SQLAlchemy, endpoints, lógica de negocio, autenticación JWT.
- **Simón Carmona** — diseño de base de datos: DER, instancia PostgreSQL en la nube, cadena de conexión. AÚN no entrega la instancia ni la cadena.
- **David Alejandro Orozco** — frontend en Angular. AÚN no empieza.

---

## 4. SPRINT ACTUAL (Sprint 2, 23–30 agosto)

Subtareas de backend de Juanca, en orden:
1. **JDS-6**: Modelo de Usuario + endpoint `POST /api/login` para dignatarios con Token JWT. ✅ **COMPLETADA** — commit `feat: implementar modelo de Usuario y login con JWT (JDS-6)` ya hecho y pusheado a `origin/feature/JDS-6-login`. Verificado en esta sesión (2026-09-01): `POST /api/login` con `juanca@test.com` / `Password1` devuelve `access_token` correctamente.
1b. **Registro de usuarios** (`POST /api/register`): ✅ **COMPLETADO** (2026-09-01, cambios SIN commitear aún). Ver detalle en sección 6b.
2. **JDS-7**: Modelo de PQRS + endpoint `GET /api/pqrs/entrantes` (listar solicitudes nuevas). ✅ **COMPLETADA** (2026-09-01, cambios SIN commitear aún). Ver detalle en sección 6c.
3. Endpoint `PUT /api/pqrs/{id}/asignar` (vincular PQRS a un comité). ← **SIGUIENTE PASO**
4. Endpoint `PUT /api/pqrs/{id}/estado` (actualizar estado En_Proceso/Finalizada).
5. Endpoint `GET /api/pqrs/historial` (registro histórico completo).

JDS-61 ("Estructura Base del Backend") ya se completó con commit/push.

---

## 5. CONVENCIONES DE TRABAJO (IMPORTANTES)

- **Modularización estricta por responsabilidad única**: cada archivo hace UNA cosa (`validaciones.py` solo valida, `seguridad.py` solo hashea/verifica, `tokens.py` solo genera JWT, `gestion.py` solo orquesta). Nunca todo junto. Aplica por dominio: `app/services/<dominio>/` (ej. `app/services/auth/`, luego `app/services/pqrs/` con el mismo patrón).
- **Juanca prefiere escribir el código él mismo** cuando puede. Se le explica qué hace cada pieza nueva y se le pide que lo intente; solo se le da el código armado cuando él dice que no sabe. Cuando se le da código, se explica **línea por línea**.
- Es aprendiz ADSO: sabe POO básica en Python (clases, herencia, encapsulación), estructuras de control, estructuras de datos, manejo de excepciones. PRIMERA vez con FastAPI, SQLAlchemy, Pydantic, JWT, passlib. Lo nuevo se explica desde cero con ejemplos.
- Prefiere respuestas **concisas, sin relleno**.

---

## 6. ESTADO DETALLADO DE JDS-6 (login con JWT) — COMPLETADA

### Decisión de campos de registro (ya tomada con el equipo)
Datos básicos del registro: **nombre completo, correo, contraseña, celular**. El **rol** (dignatario, comité, etc.) y el **comité/cargo** NO los define el usuario — los asigna un **super administrador**, y solo él los puede cambiar. Esto ya se comunicó a Simón para el DER. Tabla `users` esperada: id, full_name, email (único), hashed_password, phone, role (default 'usuario_comunidad'), committee/cargo (nullable), is_active, created_at.

### Estructura de carpetas actual
```
COMUNIXX/
├── pyproject.toml
├── .env  /  .env.example  /  .gitignore  /  uv.lock  /  dev.db
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/          __init__.py, config.py
│   ├── api/v1/routers/ auth.py
│   ├── db/            __init__.py, session.py
│   ├── models/        __init__.py, user.py
│   ├── schemas/       __init__.py, user.py, token.py
│   └── services/auth/ __init__.py, validaciones.py, seguridad.py, tokens.py, gestion.py
└── tests/            test_validaciones.py
```

### pyproject.toml — puntos ya resueltos
- `[tool.uv]` con `package = false` (la app NO es librería instalable; sin esto uv falla pidiendo `src/comunixx/__init__.py`).
- Se quitó `[project.scripts]` (no aplica).
- `requires-python` se bajó de `>=3.14` a algo más estándar.
- Se agregó `[tool.pytest.ini_options]` con `pythonpath = ["."]` (para que pytest encuentre el paquete `app`). NO afecta despliegue.

### Dependencias instaladas
Producción: `fastapi`, `uvicorn[standard]`, `pydantic-settings`, `python-dotenv`, `sqlalchemy`, `passlib[bcrypt]`, `python-jose[cryptography]`.
Dev: `pytest`, `httpx`, `ruff`.

### Base de datos (temporal)
Usando **SQLite local** (`DATABASE_URL=sqlite:///./dev.db` en `.env`) para no bloquearse mientras Simón entrega PostgreSQL. El engine en `db/session.py` usa `connect_args={"check_same_thread": False}` — esto es EXCLUSIVO de SQLite, hay que quitarlo al pasar a PostgreSQL. Al migrar, solo se cambia `DATABASE_URL` en `.env`, no se toca código.

### Archivos completados y probados
- `app/models/user.py`: modelo `User` (id, email, hashed_password, full_name, role, is_active). PENDIENTE agregar `phone` y posiblemente `committee` cuando Simón confirme el DER.
- `app/db/session.py`: engine, SessionLocal, Base, `get_db()`.
- `app/core/config.py`: `Settings(BaseSettings)` con `database_url: str` y `secret_key: str`, lee de `.env`.
- `app/schemas/user.py`: `UserLogin` (email, password) y `UserResponse` (id, email, full_name, role) — sin exponer hash.
- `app/schemas/token.py`: `Token` (access_token, token_type).
- `app/services/auth/seguridad.py`: `hash_password()` y `verify_password()` con `CryptContext(schemes=["bcrypt"])`. FUNCIONA.
- `app/services/auth/tokens.py`: `create_access_token(data: dict)` con `jose.jwt`, expiración 8h, algoritmo HS256, firma con `settings.secret_key`. FUNCIONA.
- `app/services/auth/validaciones.py`: `is_password_strong(password)` — longitud ≥8, ≥1 mayúscula, ≥1 dígito. PROBADO con pytest (4 tests OK).
- `app/services/auth/gestion.py`: `authenticate_user(db, email, password)` y `login_user(db, email, password)`. FUNCIONA.
- `app/api/v1/routers/auth.py`: `POST /login`, `Depends(get_db)`, `HTTPException(401)` si credenciales inválidas, devuelve `Token`. FUNCIONA.
- `app/main.py`: app FastAPI, CORS para `http://localhost:4200`, `include_router(auth_router, prefix="/api")`, `GET /health`. FUNCIONA.

### Usuario de prueba (ya existe en dev.db)
```
email: juanca@test.com
password: Password1
role: usuario   (default; el rol lo asigna luego el superadmin)
phone: 3001234567
```
Login verificado con `POST /api/login` → devuelve `access_token` válido. Este usuario ahora se crea vía `POST /api/register` (ya no a mano por el REPL).

### Estado de git
Rama `feature/JDS-6-login`. Commits en `origin`: `chore: Estructura base del proyecto` → `feat: implementar modelo de Usuario y login con JWT (JDS-6)`. Los cambios del registro (sección 6b) están SIN commitear todavía.

---

## 6b. REGISTRO DE USUARIOS (`POST /api/register`) — COMPLETADO 2026-09-01

Se implementó el registro que faltaba (antes solo existía login). Cambios:
- `app/models/user.py`: se agregaron columnas `phone` (nullable) y `created_at`. El default de `role` sigue siendo `"usuario"` (OJO: el CLAUDE.md original mencionaba `'usuario_comunidad'`; se dejó `"usuario"` por consistencia con la lista de 4 roles y el código previo — **confirmar con el equipo cuál es el valor correcto**).
- `app/schemas/user.py`: nuevo `UserCreate` (full_name, email, password, phone); `UserResponse` ahora incluye `phone` y usa `Config.from_attributes = True`.
- `app/services/auth/validaciones.py`: nueva `is_valid_email(email)` (regex simple).
- `app/services/auth/gestion.py`: nueva `register_user(db, full_name, email, password, phone)` — valida email y fuerza de contraseña, rechaza email duplicado (lanza `ValueError`), hashea y guarda. NO permite elegir rol (lo asigna el superadmin).
- `app/api/v1/routers/auth.py`: nuevo `POST /register` → 201 con `UserResponse`; traduce `ValueError` a `HTTPException 400`.
- `app/main.py`: se agregó `Base.metadata.create_all(bind=engine)` + import del modelo `user` (antes NO existía create_all; las tablas se creaban a mano en el REPL). Ahora las tablas se crean solas al arrancar.
- `tests/test_validaciones.py`: +4 tests para `is_valid_email` (8 tests en total, todos pasan).
- **BD**: se recreó `dev.db` con la estructura nueva (tenía la tabla vieja sin `phone`). Además `dev.db` se sacó de git (`git rm --cached`) y se agregó a `.gitignore` — una BD local no debe versionarse.

Probado end-to-end con curl: registro OK (201), login del registrado OK, y los 3 errores (email duplicado / contraseña débil / email inválido) devuelven 400 con mensaje claro.

---

## 6c. JDS-7 — MODELO PQRS + `GET /api/pqrs/entrantes` — COMPLETADO 2026-09-01

Modelo `PQRS` y endpoint que lista las solicitudes nuevas. Cambios (todos SIN commitear aún):
- `app/models/pqrs.py`: modelo `PQRS` (tabla `pqrs`). Campos: `id`, `codigo_seguimiento` (único, generado con `uuid.uuid4().hex[:10]`, para consultar sin login), `tipo` (Peticion/Queja/Reclamo/Sugerencia), `asunto`, `descripcion`, `estado` (default `"Nueva"` → `En_Proceso` → `Finalizada`), `es_anonima` (Boolean default False), `radicado_por_id` (FK a `users.id`, **nullable** — vacío para no registrados), `nombre_contacto`/`email_contacto`/`telefono_contacto` (nullable), `comite` (nullable), `created_at`, `updated_at` (con `onupdate`).
- **Decisión de diseño con Juanca**: quién radica = FK opcional + datos de contacto. Los registrados quedan con FK; turistas/no registrados solo con datos de contacto. Además `es_anonima`: se guardan los datos pero se OCULTAN en la respuesta a los dignatarios; la persona sigue el estado con su `codigo_seguimiento`. **Falta comunicar estos campos (sobre todo `es_anonima` y `codigo_seguimiento`) a Simón para el DER.**
- `app/schemas/pqrs.py`: `PQRSResponse` (incluye datos de contacto como opcionales; llegan en `None` cuando la PQRS es anónima).
- `app/services/pqrs/` (modular estricto): `consultas.py` (`obtener_entrantes` = query de estado "Nueva"), `anonimato.py` (`ocultar_si_anonima` = arma el dict y pone en None la identidad si es anónima), `gestion.py` (`listar_entrantes` = orquesta consulta + anonimato).
- `app/api/v1/routers/pqrs.py`: `GET /pqrs/entrantes`, `response_model=list[PQRSResponse]`.
- `app/main.py`: registra `pqrs_router` con prefix `/api` e importa el modelo `pqrs` para create_all.

Probado end-to-end: se insertaron 4 PQRS de prueba (normal, anónima, turista sin cuenta, y una `En_Proceso`). El GET devuelve **solo las 3 "Nueva"** (la `En_Proceso` no sale), la anónima oculta nombre/email/teléfono/FK pero conserva `codigo_seguimiento`. `pytest` 8/8 OK.

Nota lint: `ruff` marca `B008` en los endpoints por `Depends()` en los defaults — es **falso positivo**, es el patrón oficial de FastAPI, no se toca. Quedan `DTZ003` (utcnow) y `SIM103` en código previo de auth, sin corregir (funcionan).

---

## 7. SIGUIENTE PASO INMEDIATO (endpoint asignar comité)

JDS-6, registro y JDS-7 están hechos (sin commitear). Siguiente subtarea (sección 4, punto 3):
- `PUT /api/pqrs/{id}/asignar` — vincular una PQRS a un comité (setear el campo `comite`). Probablemente también cambie el estado a `En_Proceso`. Reutilizar `app/services/pqrs/` (agregar la lógica en un archivo por responsabilidad, p. ej. `gestion.py` orquesta y una función de actualización en `consultas.py` o un nuevo módulo).

Seguir la metodología de la sección 5: explicar, dejar que Juanca lo intente, revisar línea por línea solo si pide el código armado.

---

## 8. ENTORNO / MÁQUINA

- Windows, computador personal. Terminales: Git Bash (MINGW64) y PowerShell.
- Python 3.14.3, gestor `uv`.
- Se **desactivó Smart App Control** de Windows (Seguridad de Windows → Control de aplicaciones y navegador → Configuración de Control de aplicaciones inteligentes → Desactivado) porque bloqueaba `pytest.exe`. Resuelto.
- Trabajando con Claude Code directamente en la carpeta del proyecto.

---

## 9. DOCUMENTOS FUENTE (ya revisados)

Tres Word oficiales: Documento del Proyecto Integrador (RF-01 a RF-15, RNF, HU con criterios de aceptación), Documento de Épicas (5 épicas + HU + prioridad MoSCoW), Documento de Historias de Usuario detallado. HU6–HU10 (Épica 1) corresponden a las subtareas del sprint de Juanca. HU22 y RF-15 cubren registro de usuarios pero sin detallar campos exactos — el equipo los definió por su cuenta (ver sección 6).

---

## 10. CÓMO SEGUIR

JDS-6 está terminada y verificada. Continuar con JDS-7 (sección 7). Mantener convenciones de la sección 5. No repetir explicaciones ya dadas salvo que Juanca lo pida.
