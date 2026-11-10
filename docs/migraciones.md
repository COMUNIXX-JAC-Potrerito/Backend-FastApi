# Migraciones de la base de datos (Alembic)

## ¿Qué es una migración?

Una **migración** es un archivo de Python, guardado en git, que describe **un
cambio en la estructura de la base de datos**: crear una tabla, agregar una
columna, crear un índice… Es como un `git log` de la base: cada cambio queda
escrito, revisado y probado, y se aplica igual en local, en los tests y en Neon.

La herramienta es **Alembic** (la estándar con SQLAlchemy). La base guarda en
una tabla pequeña, `alembic_version`, cuál fue la última migración aplicada, y
Alembic aplica solo las que falten, en orden.

### ¿Por qué no basta `create_all`?

Hasta la v1.2.0 la app usaba `Base.metadata.create_all()`, que **crea las
tablas que faltan pero nunca modifica las existentes**. Si un modelo ganaba una
columna, en Neon había que agregarla a mano (y era fácil olvidarlo: el código
pedía una columna que no existía y la app respondía error 500).

## Cómo funciona aquí

- Las migraciones están en `migraciones/versions/`, numeradas: `0001_…`, `0002_…`.
- **Se aplican solas al arrancar la app** (`app/db/migrar.py`, llamado desde
  `app/main.py`). En Render eso pasa en cada despliegue; en local, cada vez que
  inicias `uvicorn`. No hay que hacer nada a mano.
- Una base creada antes de las migraciones (como la de Neon) tiene las tablas
  pero no `alembic_version`: la app la **marca** como que ya está en la `0001`,
  sin tocar nada, y desde ahí aplica las siguientes.
- Si una base tiene tablas propias **sin registro y con tablas o columnas
  faltantes** (p. ej. un `dev.db` viejo), la app **no arranca** y dice qué falta:
  marcarla ocultaría el problema. En local, lo más simple es borrar ese `dev.db`.
- En PostgreSQL cada migración corre dentro de una transacción: si algo falla, se
  deshace completa y la base queda como estaba. Si una migración falla en Render,
  el despliegue nuevo no arranca y la versión anterior sigue atendiendo; basta
  corregir y volver a desplegar.
- Un bloqueo de PostgreSQL evita que dos instancias migren a la vez, y si una
  tabla está ocupada más de 15 s la migración falla en vez de colgar el despliegue.

> ⚠️ **Tu `.env` decide a qué base le aplicas las migraciones.** Si su
> `DATABASE_URL` es la de Neon, iniciar `uvicorn` en local **migra Neon**. Para
> desarrollar usa `DATABASE_URL=sqlite:///./dev.db` (con `sqlite://` en memoria
> las migraciones no sirven: cada conexión ve una base distinta y vacía).

| Migración | Qué hace |
|---|---|
| `0001` | Esquema base: las 11 tablas tal como estaban en la v1.2.0. |
| `0002` | Índice único `(encuesta_id, usuario_id)`: una cuenta responde cada encuesta una sola vez, aunque lleguen dos clics a la vez. Antes borra las respuestas repetidas, conservando la primera. |

## Cambiar un modelo, paso a paso

Ejemplo: agregar `barrio` a los usuarios.

1. Edita el modelo (`app/models/user.py`):
   ```python
   barrio = Column(String, nullable=True)
   ```
2. Genera la migración. Alembic compara los modelos con una base al día y
   escribe el cambio por ti (con `DATABASE_URL=sqlite:///./dev.db`, nunca Neon):
   ```bash
   uv run python -m app.db.migrar          # deja tu base local al día
   uv run alembic revision --autogenerate --rev-id 0003 -m "barrio de los usuarios"
   ```
   Se crea `migraciones/versions/0003_barrio_de_los_usuarios.py`.
3. **Ábrela y revísala.** Alembic acierta casi siempre, pero no detecta, por
   ejemplo, un cambio de nombre (lo ve como "borrar columna + crear columna", y
   eso borraría los datos). Si la columna nueva es obligatoria (`nullable=False`)
   en una tabla con datos, la migración debe darle un valor a las filas existentes.
4. Pruébala: `uv run pytest` (el test `test_base_vacia_queda_igual_a_los_modelos`
   falla si el modelo y las migraciones no coinciden).
5. Commit del modelo **y** la migración juntos. Al desplegar, Render la aplica.

## Comandos útiles

```bash
uv run python -m app.db.migrar               # aplica las pendientes (lo mismo que al arrancar)
uv run alembic current                       # en qué migración está la base
uv run alembic history                       # lista de migraciones
uv run alembic upgrade 0001:head --sql       # muestra el SQL sin ejecutarlo
uv run alembic downgrade -1                  # deshace la última (con cuidado)
```

Todos usan la `DATABASE_URL` de tu `.env`.

## Reglas

- **Nunca edites una migración que ya se aplicó en Neon**: crea una nueva.
- Nunca cambies la base de Neon a mano: todo cambio pasa por una migración.
- Antes de desplegar una migración que borra o transforma datos, pide a quien
  administra Neon una *branch* (copia) de la base como respaldo. Es gratis.
