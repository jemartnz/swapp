![Logo](/front/public/logo-swapp.webp)

# Swapp - Plataforma de Trueques

**Swapp** es un sitio web donde las personas pueden intercambiar servicios sin dinero (por ejemplo, clases de inglés por clases de cocina). Los servicios pueden ser de cualquier rubro: educativo, doméstico, tecnológico, artístico, etc.

## Tecnologías

- **Frontend**: React 19, React Router 7, Vite 7, Bootstrap 5
- **Backend**: Flask, SQLAlchemy, Flask-JWT-Extended
- **Base de datos**: PostgreSQL 16
- **Media**: Cloudinary (fotos de perfil)
- **Despliegue**: Docker Compose (dev & prod), Render, GitHub Container Registry

## Requisitos

- [Docker](https://docs.docker.com/get-docker/) y Docker Compose

## Inicio rápido

```bash
# 1. Clonar el repositorio
git clone https://github.com/jemartnz/swapp.git
cd swapp

# 2. Crear archivos de entorno
cp back/.env.example back/.env
cp front/.env.example front/.env
cp db.env.example db.env

# 3. Levantar los servicios
docker compose up --build

# 4. Ejecutar migraciones y seed (en otra terminal)
docker compose exec backend flask db upgrade
docker compose exec backend python -m back.init.seed_data
docker compose exec backend python -m back.init.seed_users
```

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000/api
- **PostgreSQL**: localhost:5432

Los cambios en `back/` y `front/` se reflejan automáticamente (hot-reload).

## Producción

```bash
# Levantar con Docker
docker compose -f compose.prod.yml up --build

# Construir imágenes para el registry
docker build -f docker/prod/backend.Dockerfile -t ghcr.io/jemartnz/swapp-backend .
docker build -f docker/prod/frontend.Dockerfile -t ghcr.io/jemartnz/swapp-frontend .
```

En producción: Nginx sirve el frontend estático (puerto 80) y hace proxy de `/api/` al backend (Gunicorn, puerto 5000).

## Estructura del proyecto

```
.
├── back/                       # Backend (Flask)
│   ├── app.py                  # Entry point, blueprints, config
│   ├── models.py               # SQLAlchemy models
│   ├── wsgi.py                 # Gunicorn entry point
│   ├── utils.py                # APIException helper
│   ├── requirements.txt        # Python dependencies
│   ├── urls/                   # Route blueprints
│   │   ├── user.py
│   │   ├── skill.py
│   │   ├── category.py
│   │   ├── message.py
│   │   ├── exchange.py
│   │   └── rating.py
│   ├── cloudinary/             # Image upload config & routes
│   ├── init/                   # Seed data scripts
│   │   ├── seed_data.py
│   │   └── seed_users.py
│   ├── migrations/             # Alembic migrations
│   ├── rest/                   # REST Client .http test files
│   └── scripts/                # DB diagram generator
├── front/                      # Frontend (React + Vite)
│   ├── index.html              # HTML entry point
│   ├── main.jsx                # React entry point
│   ├── App.jsx                 # Router config
│   ├── vite.config.js          # Vite config
│   ├── package.json            # Node dependencies
│   ├── eslint.config.js        # ESLint config
│   ├── store.js                # Context + useReducer state
│   ├── services/api.js         # API calls
│   ├── pages/                  # Page components
│   ├── assets/components/      # Reusable components
│   ├── assets/styles/          # CSS modules
│   └── public/                 # Static assets (images, icons)
├── docker/
│   ├── dev/                    # Development Dockerfiles
│   │   ├── backend.Dockerfile
│   │   └── frontend.Dockerfile
│   └── prod/                   # Production Dockerfiles
│       ├── backend.Dockerfile  # Multi-stage: Python → Gunicorn
│       ├── frontend.Dockerfile # Multi-stage: Node build → Nginx
│       └── nginx.conf          # Nginx SPA + API proxy config
├── compose.yml                 # Docker Compose (desarrollo)
├── compose.prod.yml            # Docker Compose (producción)
├── db.env.example              # PostgreSQL credentials template
├── deploy.sh                   # Render deployment script
├── render.yaml                 # Render service config
└── Pipfile                     # Python dependencies (pipenv)
```

## API Endpoints

| Recurso    | URL base          | Métodos                        |
|------------|-------------------|--------------------------------|
| Usuarios   | `/api/users`      | GET, POST, PUT, DELETE         |
| Auth       | `/api/auth`       | POST `/login`, GET `/me`, POST `/refresh` |
| Habilidades| `/api/skills`     | GET, POST, PUT, DELETE         |
| Categorías | `/api/categories` | GET, POST, PUT, DELETE         |
| Mensajes   | `/api/messages`   | GET, POST, PUT, DELETE         |
| Intercambios| `/api/exchanges` | GET, POST, PUT, DELETE         |
| Puntuaciones| `/api/ratings`   | GET, POST, PUT, DELETE         |
| Foto perfil| `/api/users/<id>/profile-picture` | POST          |
