# Instrucciones para Simón — Base de datos PostgreSQL de COMUNIX

> Cópiale este texto a la IA que estés usando (o léelo tú directamente).
> Sirve para crear la instancia de PostgreSQL en la nube y entregar la cadena
> de conexión al backend.

---

Hola. Estoy trabajando en el proyecto COMUNIX, un sistema de gestión para la
Junta de Acción Comunal de la Vereda Potrerito (proyecto SENA - ADSO).
Necesito que me ayudes a crear la base de datos del proyecto. Contexto:

- El backend es Python con FastAPI + SQLAlchemy. La base de datos es PostgreSQL.
- Mi tarea es crear la instancia de PostgreSQL EN LA NUBE y entregar la cadena
  de conexión al compañero de backend.

QUÉ NECESITO QUE ME GUÍES A HACER, paso a paso:

1. Crear una cuenta gratuita en Neon (https://neon.tech) y crear un proyecto/
   base de datos PostgreSQL. (Si recomiendas Supabase en su lugar, explícame por qué.)
2. Obtener la CADENA DE CONEXIÓN (connection string) en formato estándar:
   postgresql://usuario:contraseña@host:5432/nombre_db?sslmode=require
3. Explicarme cómo compartir esa cadena de forma segura (no subirla a GitHub).

IMPORTANTE: NO necesito crear las tablas a mano. El backend usa SQLAlchemy con
create_all(), que crea las tablas automáticamente al arrancar. Solo necesito
la base vacía y la cadena de conexión.

De todos modos, para documentar el Diagrama Entidad-Relación (DER), estas son
las DOS tablas que el backend va a crear. Ayúdame a validar que mi DER coincide
con esto:

TABLA users:
- id: entero, llave primaria, autoincremental
- email: texto, único, obligatorio
- hashed_password: texto, obligatorio
- full_name: texto, obligatorio
- phone: texto, opcional
- role: texto, obligatorio, valor por defecto 'usuario'
  (roles posibles: usuario, administrador, superadministrador, entidad)
- is_active: booleano, por defecto verdadero
- created_at: fecha y hora, por defecto la fecha actual

TABLA pqrs:
- id: entero, llave primaria, autoincremental
- codigo_seguimiento: texto, único (código público para consultar sin login)
- tipo: texto, obligatorio (Peticion, Queja, Reclamo o Sugerencia)
- asunto: texto, obligatorio
- descripcion: texto, obligatorio
- estado: texto, obligatorio, por defecto 'Nueva'
  (estados: Nueva, En_Proceso, Finalizada)
- es_anonima: booleano, por defecto falso
- radicado_por_id: entero, llave foránea a users(id), OPCIONAL
  (queda vacío cuando la PQRS la radica alguien sin cuenta)
- nombre_contacto: texto, opcional
- email_contacto: texto, opcional
- telefono_contacto: texto, opcional
- comite: texto, opcional (comité/cargo de la JAC al que se asigna)
- created_at: fecha y hora, por defecto la fecha actual
- updated_at: fecha y hora, se actualiza al modificar

Si prefieres darme el script SQL (DDL) para crear estas tablas y así validar el
DER, aquí está la versión PostgreSQL:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    full_name VARCHAR NOT NULL,
    phone VARCHAR,
    role VARCHAR NOT NULL DEFAULT 'usuario',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE pqrs (
    id SERIAL PRIMARY KEY,
    codigo_seguimiento VARCHAR UNIQUE,
    tipo VARCHAR NOT NULL,
    asunto VARCHAR NOT NULL,
    descripcion VARCHAR NOT NULL,
    estado VARCHAR NOT NULL DEFAULT 'Nueva',
    es_anonima BOOLEAN DEFAULT FALSE,
    radicado_por_id INTEGER REFERENCES users(id),
    nombre_contacto VARCHAR,
    email_contacto VARCHAR,
    telefono_contacto VARCHAR,
    comite VARCHAR,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

Por favor guíame paso a paso, soy nuevo en esto.

---

## Plan de despliegue del proyecto (para referencia del equipo)

- **Base de datos:** Neon (PostgreSQL gratis, no expira).
- **Backend (FastAPI):** Render (Web Service, plan gratuito).
- **Frontend (Angular):** Vercel o Netlify (hosting estático gratis).

Orden: Neon (BD) → Render (backend con la cadena de Neon) → Vercel (frontend
apuntando a la URL pública del backend).
