# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Swapp** is a peer-to-peer skill exchange platform (trade services without money). Monorepo with a Flask backend (`back/`) and React frontend (`front/`). Deployed on Render at https://swapp-app.onrender.com.

## Tech Stack

- **Frontend**: React 19, React Router 7, Vite 7, Bootstrap 5, CSS modules, `@react-oauth/google`
- **Backend**: Flask, SQLAlchemy, Flask-JWT-Extended, `google-auth`, `flask-swagger` (pendiente implementar)
- **Database**: PostgreSQL (production & Docker dev), SQLite (fallback local dev)
- **Media**: Cloudinary for image uploads
- **Deployment**: Render (Gunicorn), Docker Compose (dev & prod), GitHub Container Registry

## Development (Docker)

```bash
# Start all services (db, backend, frontend)
docker compose up

# Run backend tests (SQLite in-memory, no DB service needed)
docker compose exec backend pytest
docker compose exec backend pytest --cov=back --cov-report=term-missing

# Start with rebuild
docker compose up --build

# Run migrations
docker compose exec backend flask db upgrade

# Create a new migration
docker compose exec backend flask db migrate -m "message"

# Seed database
docker compose exec backend python -m back.init.seed_data
docker compose exec backend python -m back.init.seed_users

# Frontend lint
docker compose exec frontend npm run lint
```

Services: `db` (PostgreSQL 16, port 5432), `backend` (Flask, port 5000), `frontend` (Vite, port 3000).
Source code is volume-mounted — changes to `back/` and `front/` auto-reload.

Copy `back/.env.example` to `back/.env`, `front/.env.example` to `front/.env`, and `db.env.example` to `db.env` before first run.

## Production (Docker)

```bash
# Build and run production containers
docker compose -f compose.prod.yml up --build

# Build images for registry
docker build -f docker/prod/backend.Dockerfile -t ghcr.io/<user>/swapp-backend .
docker build -f docker/prod/frontend.Dockerfile -t ghcr.io/<user>/swapp-frontend .
```

Production uses multi-stage builds: frontend builds static files served by Nginx (port 80), backend runs Gunicorn (port 5000). Nginx proxies `/api/` to the backend.

## Development (without Docker)

```bash
cd front && npm run dev   # Frontend (port 3000)
flask run                 # Backend (port 5000)
cd front && npm run build # Build frontend
./deploy.sh               # Production deploy (Render)
```

## Architecture

### Backend (`back/`)

- **Entry point**: `back/app.py` — Flask app factory, blueprint registration, serves built frontend in production (flask-admin removed in #11)
- **Models**: `back/models.py` — SQLAlchemy models (User, Category, Skill, Message, Exchange, Rating)
- **Routes**: `back/urls/` — Blueprints: `user.py`, `skill.py`, `category.py`, `message.py`, `exchange.py`, `rating.py`
- **Auth routes**: `/api/auth/login` (POST), `/api/auth/me` (GET, jwt_required), `/api/auth/refresh` (POST, jwt_required refresh=True), `/api/auth/google/verify` (POST, verifies Google id_token → returns app JWT), `/api/logout` (POST, stateless)
- **Utils**: `back/utils.py` — `APIException`, `validate()`, `success()`, `error_response()`, `not_found()`, `forbidden()`, `bad_request()`, `get_current_user()`, `paginate_query()`, `paginated_success()` helpers used across all blueprints
- **Tests**: `back/tests/` — pytest suite (SQLite in-memory + StaticPool); `conftest.py` has app/client fixtures, factory helpers, `auth_headers`; 7 test files covering auth, users, messages, exchanges, ratings, skills, categories; 125 tests total including pagination coverage
- **Image upload**: `back/cloudinary/` — Cloudinary config and profile picture route
- **Seed data**: `back/init/seed_data.py` (categories + skills), `back/init/seed_users.py` (demo users)
- **Migrations**: `back/migrations/` — Alembic/Flask-Migrate migration files
- **Scripts**: `back/scripts/` — DB diagram generator
- **HTTP tests**: `back/rest/` — REST Client `.http` files for testing endpoints
- **WSGI**: `back/wsgi.py` — Gunicorn entry point

All API endpoints prefixed with `/api/`. Auth uses JWT tokens via Flask-JWT-Extended.

### Frontend (`front/`)

- **Entry point**: `front/index.html` → `front/main.jsx` → `front/App.jsx` (routes)
- **Config**: `front/vite.config.js`, `front/package.json`, `front/eslint.config.js`
- **Static assets**: `front/public/` — images and icons
- **State management**: Context + useReducer in `front/store.js` (actions: SET_USER, SET_USERS, SET_TOKEN, SET_CATEGORIES)
- **API calls**: `front/services/api.js`
- **Pages**: Home, Login, Register, UserProfile, PublicProfile, CategoryUsers
- **Components**: Navbar, Footer, Carousel, UserCard, ChatModal, ExchangeModal, RatingModal, AddSkillModal, CropperModal, MessagingButton, ErrorBoundary
- **Styles**: `front/assets/styles/` — one CSS file per component

### Key Patterns

- JWT access token (6h) and refresh token (30d) stored in localStorage; `apiFetch()` in `services/api.js` handles silent token refresh on 401 automatically
- Google OAuth uses frontend-driven popup flow (`@react-oauth/google`): Google returns `id_token` to the browser → frontend POSTs to `/api/auth/google/verify` → backend verifies with `google-auth` and returns app JWT. No callback URL needed — works on any domain. `GOOGLE_CLIENT_ID` env var required on backend; `VITE_GOOGLE_CLIENT_ID` build ARG required for frontend Docker image
- M2M relationship between users and skills via `UserSkill` junction table
- Ratings are tied to completed exchanges via `UniqueConstraint(exchange_id, rater_id)`
- Password hashing via werkzeug property setter on `User.password`
- Vite config and all frontend files live inside `front/`; builds to `front/dist/`
- Flask serves `front/dist/` as static folder in Render production
- Docker prod: Nginx serves static files and proxies `/api/` to backend

## API Endpoints

| Resource   | Base URL          | Methods                        |
|------------|-------------------|--------------------------------|
| Users      | `/api/users`      | GET (paginated), POST, PUT, DELETE |
| Auth       | `/api/auth`       | POST `/login`, GET `/me`, POST `/refresh`, POST `/google/verify` |
| Logout     | `/api/logout`     | POST                           |
| Skills     | `/api/skills`     | GET, POST, PUT, DELETE         |
| Categories | `/api/categories` | GET, POST, PUT, DELETE         |
| Messages   | `/api/messages`   | GET (paginated), POST, PUT, DELETE |
| Exchanges  | `/api/exchanges`  | GET (paginated), POST, PUT, DELETE |
| Ratings    | `/api/ratings`    | GET (paginated), POST, PUT, DELETE |
| Upload     | `/api/users/<id>/profile-picture` | POST          |

Paginated list endpoints accept `?page=1&per_page=20` (default 20, max 100). Response: `{"data": [...], "pagination": {"page", "per_page", "total", "pages", "has_next", "has_prev"}}`.

## Environment Variables

Environment is split per service:
- `back/.env.example` — Flask, JWT, DB, Cloudinary, `GOOGLE_CLIENT_ID` vars
- `front/.env.example` — Vite vars (`VITE_BACKEND_URL`, `VITE_APP_NAME`, `VITE_GOOGLE_CLIENT_ID`)
- `db.env.example` — PostgreSQL credentials (`POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`)
- For Docker prod: `VITE_GOOGLE_CLIENT_ID` must be passed as build ARG (`--build-arg` or via `compose.prod.yml`)

### Docker structure

```
docker/
  dev/                    # Development Dockerfiles
    backend.Dockerfile    # Python 3.13 Alpine + Flask dev server
    frontend.Dockerfile   # Node 24 Alpine + Vite dev server
  prod/                   # Production Dockerfiles
    backend.Dockerfile    # Multi-stage: Python + Gunicorn (4 workers)
    frontend.Dockerfile   # Multi-stage: Node build → Nginx
    nginx.conf            # Nginx config (SPA fallback + /api/ proxy)
```

## Codebase Language

Code (variables, models, API routes) is in **English**. UI text (labels, messages) is in **Spanish**.
