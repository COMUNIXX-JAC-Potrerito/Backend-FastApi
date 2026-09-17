# Guía de despliegue de COMUNIX

Arquitectura en producción (todo gratis):

- **Base de datos:** PostgreSQL en **Neon** (✅ ya creada).
- **Backend (FastAPI):** **Koyeb** (no se duerme, gratis).
- **Frontend (Angular):** **Vercel** (estático, gratis).

Orden: **Backend (Koyeb) → poner su URL en el frontend → Frontend (Vercel) → agregar el dominio de Vercel al CORS del backend.**

---

## Parte A — Backend en Koyeb

1. El repo ya está en GitHub (`Backend-FastApi`) con un **Dockerfile** en la raíz. Koyeb lo usará para construir.
2. Crea una cuenta en <https://koyeb.com> (puedes entrar con GitHub).
3. **Create Service → GitHub** → elige el repo `Backend-FastApi` y la rama (`feature/sprint-2`).
4. Koyeb detecta el **Dockerfile** automáticamente (builder: Docker).
5. **Instance:** Free. **Port:** `8000` (el Dockerfile ya escucha en `$PORT`/8000).
6. **Environment variables** (en Koyeb, sección Variables):
   - `DATABASE_URL` = la cadena de conexión de Neon (la que te pasó Simón).
   - `SECRET_KEY` = la misma clave secreta del `.env` local.
   - `CORS_ORIGINS` = `http://localhost:4200` (más adelante le agregas el dominio de Vercel).
7. **Deploy.** Al terminar te da una URL pública tipo `https://comunix-backend-xxxx.koyeb.app`.
8. Verifica:
   - `https://<tu-backend>.koyeb.app/health` → `{"status":"ok"}`
   - `https://<tu-backend>.koyeb.app/docs` → la documentación de la API.

> Las tablas se crean solas al arrancar (create_all), contra la base de Neon.

---

## Parte B — Frontend en Vercel

1. Edita `src/environments/environment.prod.ts` y pon la URL del backend de Koyeb:
   ```ts
   export const environment = {
     apiUrl: 'https://<tu-backend>.koyeb.app/api',
   };
   ```
   Haz `git commit` y `git push` (rama `master`).
2. Crea una cuenta en <https://vercel.com> (entra con GitHub).
3. **Add New → Project** → importa el repo `Frontend-Angular`.
4. Framework: **Angular** (Vercel lo detecta). Deja el build por defecto (`ng build`). El `vercel.json` ya maneja el ruteo del SPA.
5. **Deploy.** Te da una URL tipo `https://comunix.vercel.app`.

---

## Parte C — Conectar CORS

1. Vuelve a Koyeb → variables de entorno → edita:
   - `CORS_ORIGINS` = `https://<tu-frontend>.vercel.app,http://localhost:4200`
2. **Redeploy** del backend en Koyeb.
3. Abre `https://<tu-frontend>.vercel.app` y prueba login/PQRS: ya funciona en la nube.

---

## Crear el primer superadministrador

El endpoint de cambio de rol solo lo puede usar un superadministrador, y al inicio no hay ninguno. Para crear el primero:

1. Regístrate en la app (o con `POST /api/register`).
2. Desde tu máquina local (el `.env` local ya apunta a Neon), ejecuta:
   ```bash
   uv run python crear_superadmin.py tu-correo@ejemplo.com
   ```
   Eso promueve ese usuario a `superadministrador` en la base de Neon.

---

## Seguridad

- Cuando todo esté estable, pídele a Simón **rotar la contraseña** de la base en Neon (se compartió por chat) y actualiza `DATABASE_URL` en el `.env` local y en las variables de Koyeb.
- El `.env` nunca se sube a git; en producción los secretos van en las **variables de entorno** de Koyeb.
