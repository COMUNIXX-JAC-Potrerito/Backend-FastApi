# Historial de cambios — COMUNIX Backend (FastAPI)

Todos los cambios relevantes del backend se registran aquí. Formato basado en
[Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/); las versiones siguen
[Versionado Semántico](https://semver.org/lang/es/) y cada una tiene su etiqueta en Git.

## [Sin publicar]

### Cambiado
- **RN-012 aplicada en el servidor:** un administrador ya no puede cambiar el comité de
  una PQRS que ya tiene uno (HTTP 409). Solo un superadministrador puede corregir una
  asignación. Antes la regla solo la imponía la interfaz.

### Agregado
- Licencia MIT (`LICENSE`) y este historial de cambios.

## [1.3.1] — 2026-11-10

### Corregido
- CORS para el nuevo proyecto del frontend en Vercel (`https://comunix.vercel.app` y sus
  vistas previas). La URL anterior (`frontend-angular-comunixx.vercel.app`) dejó de existir.

## [1.3.0] — 2026-11-10

### Agregado
- Migraciones de base de datos con **Alembic** (`migraciones/`), aplicadas al arrancar
  la aplicación. Revisión `0002`: una respuesta por cuenta en cada encuesta (índice único).
- Prueba de las migraciones contra PostgreSQL 18 en la integración continua.

## [1.2.0] — 2026-11-10

### Seguridad
- Segunda auditoría: **PyJWT** y **bcrypt** en lugar de `python-jose` y `passlib`.
- Límites de frecuencia por IP y bloqueo temporal del login por cuenta.
- IP real del cliente detrás de Cloudflare y Render (`PROXIES_CONFIABLES`).
- Cabeceras HTTP de seguridad y tamaño máximo de petición (12 MB).
- Verificación del tipo real de los adjuntos y nombre genérico en PQRS anónimas.

## [1.1.0] — 2026-11-09

### Seguridad
- Primera auditoría de seguridad y calidad del backend.

## [1.0.0] — 2026-11-09

Primera entrega en producción (Render + Neon). Incluye:
- Autenticación JWT, registro y roles (usuario, administrador, superadministrador, entidad).
- PQRS: radicación pública o anónima con adjuntos (Cloudinary), código de seguimiento,
  asignación a comités (Ley 2166 de 2021), estados Nueva / En_Proceso / En_Espera /
  Finalizada y varias respuestas por PQRS con edición de 5 minutos.
- Publicaciones, mensajería interna entre dignatarios, bitácora de comunicaciones,
  envío masivo por correo, encuestas y censos, y reportes (incluida la carga por comité).

[Sin publicar]: https://github.com/COMUNIXX-JAC-Potrerito/Backend-FastApi/compare/v1.3.1...develop
[1.3.1]: https://github.com/COMUNIXX-JAC-Potrerito/Backend-FastApi/compare/v1.3.0...v1.3.1
[1.3.0]: https://github.com/COMUNIXX-JAC-Potrerito/Backend-FastApi/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/COMUNIXX-JAC-Potrerito/Backend-FastApi/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/COMUNIXX-JAC-Potrerito/Backend-FastApi/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/COMUNIXX-JAC-Potrerito/Backend-FastApi/releases/tag/v1.0.0
