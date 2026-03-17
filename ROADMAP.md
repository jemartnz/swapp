# ROADMAP — Swapp

Roadmap of improvements based on code analysis. Organized by priority.

---

## P0 — Critical (Security)

- [x] **Add `@jwt_required()` to all mutating endpoints** [#2](https://github.com/jemartnz/swapp/issues/2)
  - `DELETE /api/users/<id>`
  - `PUT /api/users/<id>`
  - `POST /api/users/<id>/skill`
  - All message endpoints (`POST`, `PUT`, `DELETE`)
  - All exchange endpoints (`POST`, `PUT`, `DELETE`)
  - All rating endpoints (`POST`, `PUT`, `DELETE`)
  - `POST /api/users/<id>/profile-picture`

- [x] **Add ownership authorization checks** [#3](https://github.com/jemartnz/swapp/issues/3)
  - After verifying JWT, compare `get_jwt_identity()` email with the resource owner
  - Users should only modify their own profile, skills, and messages
  - Only exchange participants should be able to complete/delete exchanges

- [x] **Stop leaking internal errors to clients** [#4](https://github.com/jemartnz/swapp/issues/4)
  - Replace `"detail": str(e)` in all catch blocks with a generic message in production
  - Use `app.config["DEBUG"]` to conditionally include details

---

## P1 — High (Bugs & Data Integrity)

- [x] **Fix N+1 query in `User.rating_average`** [#5](https://github.com/jemartnz/swapp/issues/5)
  - The `rating_average` property runs a full DB query per user
  - When listing 100 users, this generates 101 queries
  - Options: eager loading, denormalized `avg_rating` column, or SQL subquery in the list endpoint

- [x] **Remove auto-creation of users in `/api/auth/me`** [#6](https://github.com/jemartnz/swapp/issues/6)
  - Currently, any valid JWT with an unknown email creates a new user with empty fields
  - Return 404 instead, and handle registration through the proper `/api/users` endpoint

- [x] **Add input validation to all endpoints** [#7](https://github.com/jemartnz/swapp/issues/7)
  - Validate email format, password strength, required fields
  - Validate `score` range (1-5) in ratings
  - Validate date formats before parsing

---

## P2 — Medium (Code Quality)

- [x] **Standardize API response structure** [#8](https://github.com/jemartnz/swapp/issues/8)
  - Define a consistent format: `{"data": ..., "message": "..."}` for success, `{"error": "..."}` for errors
  - Create a response helper in `utils.py`

- [x] **Add a refresh token endpoint** [#9](https://github.com/jemartnz/swapp/issues/9)
  - `create_refresh_token()` is generated at login but there's no endpoint to use it
  - Add `POST /api/auth/refresh` with `@jwt_required(refresh=True)`

- [x] **Configure OAuth properly or remove it** [#10](https://github.com/jemartnz/swapp/issues/10)
  - `OAuth()` is initialized in `app.py` but never configured
  - Either implement Google OAuth backend flow or remove the import

- [x] **Remove unused dependencies from Pipfile** [#11](https://github.com/jemartnz/swapp/issues/11)
  - `flask-swagger` — never imported
  - `flask-dance` — never imported
  - `oauthlib` — never imported
  - `wtforms` — only used by flask-admin (auto-dependency)
  - `mysqlclient` in dev — project uses PostgreSQL

- [x] **Reduce code duplication in route handlers** [#12](https://github.com/jemartnz/swapp/issues/12)
  - Added `forbidden()` and `bad_request()` helpers to `utils.py`
  - Replaced 13× inline `jsonify({"error": "Forbidden"}), 403` with `forbidden()` across all blueprints
  - Replaced inline 400/404 patterns with `bad_request()` / `not_found()`
  - Removed `jsonify` import from blueprints that no longer need it directly
  - Fixed naming conflict: renamed `/api/auth/me` handler to `get_me` (was shadowing `get_current_user` utility)
  - Standardized `cloudinary/routes.py` to use `success()` instead of bare `jsonify()`

- [x] **Handle `/api/auth/me` errors in frontend** [#22](https://github.com/jemartnz/swapp/issues/22)
  - All 7 call sites do not check `response.ok` before dispatching to the store
  - On 401/404: call `localStorage.removeItem("token")` to clear stale token
  - Do not dispatch `SET_USER` with an error payload
  - Files: `Home.jsx`, `UserProfile.jsx`, `PublicProfile.jsx` (×2), `ChatModal.jsx`, `ExchangeModal.jsx`, `RatingModal.jsx`

- [x] **Add backend tests** [#13](https://github.com/jemartnz/swapp/issues/13)
  - pytest + pytest-flask + pytest-cov in Pipfile [dev-packages] and requirements.txt
  - SQLite in-memory with StaticPool — no external DB needed for tests
  - `back/tests/conftest.py`: app fixture (function-scoped), factory helpers, `auth_headers`
  - 7 test files: `test_auth`, `test_users`, `test_messages`, `test_exchanges`, `test_ratings`, `test_skills`, `test_categories`
  - Cloudinary and Google OAuth mocked with `unittest.mock.patch`
  - Run with: `pytest` (local) or `docker compose exec backend pytest` (Docker)

---

## P3 — Low (Enhancements)

- [x] **Add pagination to list endpoints** [#14](https://github.com/jemartnz/swapp/issues/14)
  - Added `paginate_query()` and `paginated_success()` helpers to `utils.py`
  - Paginated: `GET /api/users`, `GET /api/users/category/<id>`, `GET /api/messages/<id>/sent`, `GET /api/messages/<id>/received`, `GET /api/exchanges` (all 4 variants), `GET /api/ratings`
  - Response: `{"data": [...], "pagination": {"page", "per_page", "total", "pages", "has_next", "has_prev"}}`
  - Accept `?page=1&per_page=20` (default), max 100 per page
  - Added 5 pagination tests across test_users, test_messages, test_exchanges, test_ratings
  - Frontend updated to read `.data` from all list responses (fixes pre-existing data-unwrapping bugs)

- [x] **Add frontend error boundary** [#15](https://github.com/jemartnz/swapp/issues/15)
  - Created `front/assets/components/ErrorBoundary.jsx` — class component with `getDerivedStateFromError` + `componentDidCatch`
  - Fallback UI in Spanish: "Algo salió mal" with "Reintentar" and "Volver al inicio" buttons
  - Per-route boundaries in `App.jsx` (scoped: only the erroring page falls back)
  - Global boundary in `main.jsx` (catches errors in providers/routing infrastructure)

- [ ] **Improve Vite proxy setup** [#16](https://github.com/jemartnz/swapp/issues/16)
  - Configure Vite `server.proxy` to forward `/api` requests to the backend
  - Eliminates CORS in development and simplifies frontend API calls

- [ ] **Add database indexes** [#17](https://github.com/jemartnz/swapp/issues/17)
  - Index on `messages.sender_id` and `messages.receiver_id` for chat queries
  - Index on `exchanges.offerer_id` and `exchanges.demander_id`
  - Index on `ratings.rated_id` for rating average calculation

- [ ] **Add WebSocket for real-time messaging** [#18](https://github.com/jemartnz/swapp/issues/18)
  - Current chat uses polling or page refresh
  - Flask-SocketIO or a separate WebSocket service for live updates

- [ ] **Add Swagger interactive API documentation** [#19](https://github.com/jemartnz/swapp/issues/19)
  - `flask-swagger` is already installed in Pipfile
  - Annotate all blueprints (users, skills, categories, messages, exchanges, ratings) with OpenAPI/Swagger spec
  - Serve interactive Swagger UI at `/api/docs`
  - Document request bodies, response shapes, auth headers, and error codes

---

## Completed

- [x] **Docker Compose setup** — 3 containers (db, backend, frontend) with hot-reload volumes
- [x] **Refactor codebase to English** — All models, routes, API endpoints, frontend variables
- [x] **Fix `datetime.now()` defaults** — Changed to `lambda` to avoid shared timestamp bug
- [x] **Fix `APIException` error handler** — Now accepts error param and returns proper JSON
- [x] **Fix status 204 returning JSON** — Changed to status 200
- [x] **Fix operator precedence bug** — Added parentheses and `elif` in skill association
- [x] **Fix copy-paste error messages** — Corrected IntegrityError messages per resource
- [x] **Remove dead code after `get_or_404()`** — Removed unreachable `if not` checks
- [x] **Fix `vite.config.js`** — Removed invalid `server.root`, added Docker-friendly config
