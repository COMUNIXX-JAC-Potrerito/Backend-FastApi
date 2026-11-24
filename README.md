# COMUNIX — Backend (API REST)

Sistema de Gestión y Comunicación Comunitaria para la **Junta de Acción Comunal (JAC) de la
Vereda Potrerito**. Este repositorio contiene la API REST en **Python + FastAPI**; el
frontend Angular está en
[COMUNIXX_JAC_POTRERITO](https://github.com/COMUNIXX-JAC-Potrerito/COMUNIXX_JAC_POTRERITO).

Proyecto formativo — SENA, Tecnología en Análisis y Desarrollo de Software (ADSO), ficha 3223873.

| Producción | URL |
|---|---|
| Aplicación (frontend) | <https://comunix.vercel.app> |
| API | <https://comunix-backend.onrender.com> |
| Documentación interactiva de la API (OpenAPI) | <https://comunix-backend.onrender.com/docs> |
| Verificación de salud | <https://comunix-backend.onrender.com/health> |

## Qué hace

- **PQRS:** radicación pública o anónima con adjuntos, código de seguimiento, asignación a
  los cargos y comisiones de la JAC (Ley 2166 de 2021), estados *Nueva → En proceso ⇄ En espera
  → Finalizada* y varias respuestas por solicitud.
- **Publicaciones** (decisiones, actividades, contenido institucional), **encuestas y censos**,
  **mensajería interna** entre dignatarios, **bitácora de comunicaciones** externas,
  **envío masivo** por correo y **reportes** (incluida la carga de trabajo por comité).
- **Seguridad:** JWT, cuatro roles (usuario, administrador, superadministrador, entidad),
  anonimato aplicado en el servidor, límites de frecuencia, bloqueo de login, cabeceras de
  seguridad y verificación del tipo real de los adjuntos.

## Tecnologías

Python 3.14 · FastAPI · SQLAlchemy 2 · Alembic · PostgreSQL 18 (Neon; SQLite en local) ·
PyJWT + bcrypt · Cloudinary · Pytest · Ruff · Docker · Render · GitHub Actions.
Las dependencias se gestionan con [uv](https://docs.astral.sh/uv/) (`pyproject.toml` + `uv.lock`).

## Estructura

```
app/
  main.py              # aplicación: middlewares, errores, routers y /health
  api/deps.py          # autenticación y autorización (requiere_roles)
  api/v1/routers/      # endpoints por módulo (auth, pqrs, encuestas, ...)
  core/                # configuración, errores, límites, cabeceras, logs
  db/                  # sesión de base de datos y migración al arrancar
  models/              # tablas (SQLAlchemy)
  schemas/             # validación de entrada y salida (Pydantic)
  services/<dominio>/  # reglas de negocio (RN-001 a RN-014)
migraciones/           # migraciones de Alembic
tests/                 # pruebas automatizadas (Pytest)
docs/                  # guías técnicas y documentación del proyecto
```

## Instalación y ejecución local

Requisitos: Python 3.14 y [uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
uv sync                      # instala las dependencias exactas de uv.lock
cp .env.example .env         # y completa los valores (ver comentarios del archivo)
uv run uvicorn app.main:app --reload
```

La API queda en <http://127.0.0.1:8000> y su documentación en <http://127.0.0.1:8000/docs>.
Al arrancar se aplican solas las migraciones pendientes (ver [docs/migraciones.md](docs/migraciones.md)).

> ⚠️ Si tu `.env` apunta a la base de datos de producción (Neon), ejecutar la API en local
> **migra producción**. Para desarrollar usa `DATABASE_URL=sqlite:///./dev.db`.

Primer superadministrador (después de registrarse por `POST /api/register`):

```bash
uv run python crear_superadmin.py correo@ejemplo.com
```

## Pruebas y calidad

```bash
uv run pytest                # pruebas automatizadas (unitarias y de integración)
uv run ruff check .          # análisis estático (incluye reglas de seguridad)
uv run ruff format --check . # formato
```

La integración continua ([.github/workflows/ci.yml](.github/workflows/ci.yml)) ejecuta lo
anterior en cada push y pull request, prueba las migraciones contra PostgreSQL 18 y audita
las dependencias con `pip-audit`.

## Despliegue

Render construye la imagen Docker desde la rama `master` (`render.yaml`) y la base de datos
está en Neon. Paso a paso, variables de entorno y CORS: [docs/despliegue.md](docs/despliegue.md).

## Flujo de trabajo

Git Flow (`master`, `develop`, `feature/*`, `release/*`, `hotfix/*`): ver
[CONTRIBUTING.md](CONTRIBUTING.md). Los cambios de cada versión están en
[CHANGELOG.md](CHANGELOG.md).

## Equipo

| Integrante | Rol |
|---|---|
| Juan Camilo Montes Velásquez | Líder del proyecto y desarrollador backend |
| Simón Carmona Toro | Administrador de base de datos, documentación y soporte full-stack |
| David Alejandro Orozco | Desarrollador frontend y diseñador UX/UI |

Cliente: Junta de Acción Comunal de la Vereda Potrerito.

## Uso de inteligencia artificial

En el desarrollo se usó asistencia de IA (Claude Code) para auditorías de seguridad, pruebas
automatizadas, documentación y parte de la implementación. El equipo revisó los cambios y es
responsable del código entregado.

## Licencia

[MIT](LICENSE) © 2026 equipo COMUNIX.
