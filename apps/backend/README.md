# 🩺 SaludAlDía Backend — Django + Supabase/PostgreSQL

Backend del sistema **SaludAlDía**, construido con **Django** y conectado a una base de datos **PostgreSQL** gestionada en **Supabase**. Este documento describe el estado real del backend en la rama actual.

---

## 🔐 Estado de autenticación actual

Esta generación del MVP **funciona sin JWT**. Los usuarios se identifican pasando su identidad como parámetro de consulta en cada request:

```
?email=usuario@ejemplo.com
```
o
```
?rut=12345678-9
```

Actualmente **no se utiliza**:

- `request.user`
- Encabezado `Authorization: Bearer ...`
- Access tokens
- Refresh tokens

Cada endpoint resuelve el usuario manualmente en el backend (`UserService.get_user_by_identifier`) a partir del email o rut recibido, sin sesión ni token de por medio.

> **JWT y autenticación mediante tokens quedan planificados como funcionalidad futura — próxima generación.** Ver sección [Trabajo futuro](#-trabajo-futuro).

---

## 🛠️ Stack tecnológico

- **Python 3.12**
- **Django 5.1**
- **Django REST Framework**
- **PostgreSQL** (Supabase)
- **Supabase Storage** (documentos médicos e imágenes de perfil)
- **Postman** para pruebas manuales de la API

`djangorestframework-simplejwt` está instalado en el proyecto pero **no forma parte del flujo activo actual** — ver [Trabajo futuro](#-trabajo-futuro).

---

## 📁 Estructura relevante del proyecto

```txt
apps/backend/
├── manage.py
├── requirements.txt
├── schema.sql                 ← tablas administradas manualmente en Supabase
├── test_db_queries.py         ← script de verificación manual de modelos/consultas
├── .env.example                ← plantilla de variables de entorno
├── Postman Collection/
│   ├── Saludaldia_corregida.postman_collection.json
│   └── Saludaldia_documents_updated.postman_collection.json
├── saludaldia/                ← settings, urls raíz, wsgi
└── apps/
    ├── users/          ← funcional: auth, perfil médico, imagen, account settings
    ├── documents/      ← funcional: documentos médicos, categorías, storage
    ├── sharing/        ← funcional: links temporales de documentos
    ├── health_centers/ ← stub (modelo listo, vista placeholder, sin lógica de negocio)
    ├── ai_analysis/    ← stub (modelo listo, vista placeholder, sin lógica de negocio)
    ├── pets/           ← en desarrollo (modelo aún vacío, sin tabla migrada)
    └── audit/          ← instalada en el proyecto, sin rutas registradas todavía
```

---

## 🗄️ Base de datos

El proyecto usa **Supabase PostgreSQL**. Algunas tablas son creadas por Django mediante migraciones y otras se crean manualmente con `schema.sql`:

- **Administradas por Django** (`python manage.py migrate`): `users`, `medical_profiles`.
- **Administradas manualmente vía `schema.sql`**: `document_categories`, `documents`, `health_centers`, `audit_logs`, `temporary_access_links`, `ai_recommendations`.

Estas últimas tienen modelos Django con `managed = False`: Django puede leerlas y consultarlas por ORM, pero no las crea ni modifica con migraciones. `schema.sql` debe ejecutarse manualmente en Supabase al configurar el proyecto por primera vez.

---

## ⚙️ Instalación y ejecución local

### Windows — PowerShell

```powershell
cd apps\backend
py -3.12 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
Copy-Item .env.example .env
```

Editar `.env` con los datos reales de Supabase/PostgreSQL antes de continuar.

```powershell
python manage.py migrate
python manage.py check
python manage.py runserver 8000
```

### Linux / macOS

Los mismos pasos, con la sintaxis habitual de shell:

```bash
cd apps/backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py check
python manage.py runserver 8000
```

El backend queda disponible en `http://127.0.0.1:8000/`.

---

## 🔑 Variables de entorno

Variables definidas en `.env.example`:

| Variable | Descripción |
|---|---|
| `SECRET_KEY` | Clave secreta de Django |
| `DEBUG` | Modo debug de Django |
| `ALLOWED_HOSTS` | Hosts permitidos |
| `DB_NAME` | Nombre de la base de datos |
| `DB_USER` | Usuario de PostgreSQL |
| `DB_PASSWORD` | Password de PostgreSQL |
| `DB_HOST` | Host de PostgreSQL o pooler de Supabase |
| `DB_PORT` | Puerto de PostgreSQL |
| `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` | Reservada para JWT — funcionalidad futura, no usada por el flujo actual |
| `JWT_REFRESH_TOKEN_LIFETIME_DAYS` | Reservada para JWT — funcionalidad futura, no usada por el flujo actual |
| `SUPABASE_URL` | URL del proyecto Supabase |
| `SUPABASE_SERVICE_KEY` | Service role key para operaciones backend |
| `SUPABASE_BUCKET` | Bucket por defecto configurado para archivos médicos |
| `ANTHROPIC_API_KEY` | Reservada para el módulo de IA (`ai_analysis`), todavía no implementado |
| `FRONTEND_URL` | URL del frontend, usada para CORS y para construir los links de compartir |
| `EMAIL_HOST` / `EMAIL_PORT` / `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | Configuración de SMTP; el envío real de emails todavía no está implementado en el código |

**Importante:**

- `.env` contiene credenciales reales y **no debe subirse al repositorio**.
- Las claves de Supabase (`SUPABASE_SERVICE_KEY`) deben permanecer exclusivamente en el backend.
- Ninguna credencial de Supabase debe colocarse en el frontend.

---

## ✅ Funcionalidades actuales

Implementadas y probadas manualmente vía Postman:

- Registro de usuario
- Login (validación de email/password)
- Consulta de usuario (`/me/`) por email o rut
- Recuperación de contraseña (solicitud y confirmación; valida existencia del usuario — el envío real de email aún no está implementado)
- Perfil médico (consulta y actualización)
- Imagen de perfil (subida, consulta y eliminación en Supabase Storage)
- Configuración de cuenta (actualizar nombre, cambiar contraseña)
- Documentos médicos: listado, creación, detalle, eliminación lógica
- Categorías de documentos
- Subida de documentos a Supabase Storage
- Visualización de documentos mediante signed URL temporal
- Descarga de documentos mediante signed URL temporal
- Creación de links temporales para compartir documentos
- Consulta pública de un link compartido mediante token

---

## 🔌 Endpoints actuales

Todos los endpoints que requieren usuario aceptan `?email=` o `?rut=` como identificador (no requieren token).

### Auth / Users (`/api/auth/`)

| Método | Ruta |
|---|---|
| POST | `/api/auth/register/` |
| POST | `/api/auth/login/` |
| GET | `/api/auth/me/` |
| GET, PATCH | `/api/auth/profile/` |
| POST | `/api/auth/password-reset/request/` |
| POST | `/api/auth/password-reset/confirm/` |
| GET, POST, DELETE | `/api/auth/profile/image/` |
| GET, PATCH | `/api/auth/account/settings/` |

### Documents (`/api/documents/`)

| Método | Ruta |
|---|---|
| GET | `/api/documents/categories/` |
| GET, POST | `/api/documents/` |
| GET, DELETE | `/api/documents/<document_id>/` |
| PUT | `/api/documents/<document_id>/` — **no implementado, responde 501** |
| GET | `/api/documents/<document_id>/download/` |
| GET | `/api/documents/<document_id>/view/` |

### Sharing (`/api/sharing/`)

| Método | Ruta |
|---|---|
| POST | `/api/sharing/` |
| GET | `/api/sharing/<token>/` |

### Otras apps

`/api/ai/`, `/api/health-centers/` y `/api/pets/` están registradas en `saludaldia/urls.py` pero exponen únicamente una vista placeholder de estado (`health`), sin lógica de negocio implementada. La app `audit` no tiene rutas registradas todavía.

---

## 📦 Supabase Storage

- Bucket `profile-images`: fotos de perfil de usuario.
- Buckets `documents-recetas-medicas`, `documents-examenes`, `documents-certificados`: documentos médicos, seleccionados según la categoría del documento al subirlo.
- El archivo se almacena en Storage; la metadata (bucket, key, tipo, tamaño) se guarda en PostgreSQL.
- Descarga y visualización usan **signed URLs temporales** generadas bajo demanda (no URLs públicas permanentes).

---

## 🧪 Pruebas

- `python manage.py check` se usa para validar la configuración del proyecto.
- Las pruebas de endpoints se realizan principalmente mediante **Postman**.
- **No existe todavía una suite automatizada de pytest** para este backend.

Colecciones Postman actuales:

```
apps/backend/Postman Collection/Saludaldia_corregida.postman_collection.json
apps/backend/Postman Collection/Saludaldia_documents_updated.postman_collection.json
```

---

## 🚧 Trabajo futuro

- **JWT y autenticación mediante tokens** (access/refresh, `Authorization: Bearer`) en una próxima generación del proyecto.
- Sustitución progresiva de la identificación por `email`/`rut` en query params por usuario autenticado (`request.user`).
- Suite de tests automatizados (pytest / pytest-django).
- Implementación completa de los módulos todavía en desarrollo o stub: `pets`, `health_centers`, `ai_analysis`, `audit`.
- Envío real de emails para el flujo de recuperación de contraseña.
- Revisión de seguridad y estrategia de despliegue previa a producción.
