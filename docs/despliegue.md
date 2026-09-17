# Guía de despliegue de COMUNIX

Arquitectura en producción (todo gratis):

- **Base de datos:** PostgreSQL en **Neon** (✅ ya creada).
- **Backend (FastAPI):** **Render** + un "pinger" para que no se duerma.
- **Frontend (Angular):** **Vercel** (estático, gratis).

> Nota: se descartó **Koyeb** porque se fusionó con Mistral y quitó el hosting web gratuito.

Orden: **Backend (Render) → poner su URL en el frontend → Frontend (Vercel) → agregar el dominio de Vercel al CORS del backend.**

---

## ✅ URLs EN PRODUCCIÓN (LIVE — todo desplegado)

| Pieza | URL |
|---|---|
| **Frontend (app)** | <https://frontend-angular-comunixx.vercel.app> ← URL oficial (estable, sin hash) |
| **Backend (API)** | <https://comunix-backend.onrender.com> |
| **Docs de la API** | <https://comunix-backend.onrender.com/docs> |
| **Health check** | <https://comunix-backend.onrender.com/health> |
| **Base de datos** | Neon (PostgreSQL) |
| **Monitor uptime** | UptimeRobot → HTTP a `/health` cada 5 min |

**Notas de CORS:** el backend acepta cualquier `*.vercel.app` por regex (`cors_origin_regex`), así que las URLs de deploy de Vercel nunca rompen el login. ⚠️ Si algún día se pone un **dominio personalizado** (ej. `comunixpotrerito.com`), hay que **agregarlo al `CORS_ORIGINS`** del backend en Render, porque el regex solo cubre `.vercel.app`.

**Nota del `/health`:** responde a `GET` **y** `HEAD` (UptimeRobot y varios monitores usan `HEAD`; si solo aceptara `GET` darían 405 y marcarían el server como caído).

---

## Parte A — Backend en Render

El repo `Backend-FastApi` ya tiene un **Dockerfile** y un **`render.yaml`** (Blueprint) en la raíz.

1. Entra a <https://render.com> y regístrate con **GitHub**.
2. **New +** → **Blueprint** → conecta el repo **`Backend-FastApi`**. Render lee `render.yaml` y crea el servicio `comunix-backend` (Docker, plan Free).
   - _Alternativa manual:_ **New +** → **Web Service** → repo `Backend-FastApi` → rama `master` → Render detecta el Dockerfile → plan **Free**.
3. Te pedirá las **variables de entorno** (son secretas):
   - `DATABASE_URL` = la cadena de conexión de Neon.
   - `SECRET_KEY` = la misma clave del `.env` local.
   - `CORS_ORIGINS` = tu URL de Vercel (ej. `https://frontend-angular-comunixx.vercel.app`). Si aún no la tienes, pon `http://localhost:4200` y la actualizas después.
4. **Deploy.** Tarda unos minutos (construye el Docker). Te da una URL tipo `https://comunix-backend.onrender.com`.
5. Verifica:
   - `https://<tu-backend>.onrender.com/health` → `{"status":"ok"}`
   - `https://<tu-backend>.onrender.com/docs` → la documentación de la API.

> Las tablas se crean solas al arrancar (create_all), contra la base de Neon.

### Que no se duerma (pinger)

El plan Free de Render duerme el servicio tras 15 min sin tráfico. Para evitarlo:

1. Entra a <https://uptimerobot.com> y crea una cuenta gratis.
2. **Add New Monitor** → tipo **HTTP(s)** → URL `https://<tu-backend>.onrender.com/health` → intervalo **5 minutos**.
3. Listo: lo golpea cada 5 min y nunca se duerme.

---

## Parte B — Frontend en Vercel

1. Edita `src/environments/environment.prod.ts` y pon la URL del backend de Render:
   ```ts
   export const environment = {
     apiUrl: 'https://<tu-backend>.onrender.com/api',
   };
   ```
   Haz `git commit` y `git push` (rama `master`). Vercel redespliega solo.
2. (Si aún no lo hiciste) en <https://vercel.com> importa el repo `Frontend-Angular`, framework **Angular**, y **Deploy**. El `vercel.json` ya maneja el ruteo del SPA.
3. Te da una URL tipo `https://comunix.vercel.app`.

---

## Parte C — Conectar CORS

1. Vuelve a Render → tu servicio → **Environment** → edita:
   - `CORS_ORIGINS` = `https://<tu-frontend>.vercel.app,http://localhost:4200`
2. Guarda → Render redespliega el backend solo.
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

- Cuando todo esté estable, pídele a Simón **rotar la contraseña** de la base en Neon (se compartió por chat) y actualiza `DATABASE_URL` en el `.env` local y en las variables de Render.
- El `.env` nunca se sube a git; en producción los secretos van en las **variables de entorno** de Render.
