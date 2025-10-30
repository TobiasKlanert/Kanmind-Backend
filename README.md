Kanmind Backend (Django + DRF)

Kanmind is a lightweight Kanban backend built with Django and Django REST Framework. It provides authentication via email + token, boards with members, tasks with status/priority, and task comments. This README explains setup, configuration, and the available API endpoints so you can run it locally or prepare it for production.

Features

- Authentication with email + password, DRF Token auth
- Custom `User` model (`auth_app.User`) with `fullname`
- Boards with owner and members
- Tasks with status, priority, assignee, reviewer, due date
- Task comments and comment counters
- CORS support for a frontend (defaults to `http://127.0.0.1:5500`)

Tech Stack

- Python, Django 5, Django REST Framework
- SQLite by default (easy local dev)
- Token Authentication (`rest_framework.authtoken`)

Requirements

- Python 3.10+ (3.11 recommended)
- pip / venv

Getting Started (Local)

1) Clone and enter the project directory

```
git clone https://github.com/TobiasKlanert/Kanmind-Backend.git
cd Kanmind-Backend
```

2) Create and activate a virtual environment

```
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

3) Install dependencies

```
pip install -r requirements.txt
```

4) Apply database migrations

```
python manage.py migrate
```

5) (Optional) Create an admin user to access `/admin/`

```
python manage.py createsuperuser
```

6) Run the development server

```
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`.

Configuration

All settings live in `core/settings.py`.

- `SECRET_KEY`: Currently hardcoded for development. For production, set this from an environment variable and keep it secret.
- `DEBUG`: Set to `True` for development. Must be `False` in production.
- `ALLOWED_HOSTS`: Add your domain(s) or IPs for production.
- `DATABASES`: Uses SQLite by default. Switch to Postgres/MySQL for production.
- `CORS_ALLOWED_ORIGINS`: Add your frontend origin(s). Defaults to `http://127.0.0.1:5500`.
- `REST_FRAMEWORK.DEFAULT_AUTHENTICATION_CLASSES`: Uses Token Authentication.

Note: The project does not currently read a `.env` file. If you want environment‑based config, integrate a package like `django-environ` and update `core/settings.py` accordingly.

Authentication Overview

- Uses DRF Token Authentication. After registering or logging in, include the token in requests:

```
Authorization: Token <your_token_here>
```

API Endpoints

Base paths are defined in `core/urls.py`.

- Admin
  - `GET /admin/` – Django admin site

- Auth (`auth_app.api.urls`)
  - `POST /api/registration/` – Register a new user
    - Body: `{ "fullname": str, "email": str, "password": str, "repeated_password": str }`
    - Response: `{ token, fullname, email, user_id }`
  - `POST /api/login/` – Login with email + password
    - Body: `{ "email": str, "password": str }`
    - Response: `{ token, fullname, email, user_id }`
  - `GET /api/email-check/?email=<email>` – Check if a user exists (requires auth)

- Boards (`board_app.api.urls`)
  - `GET /api/boards/` – List boards where you are owner or member (auth required)
  - `POST /api/boards/` – Create a board (auth required)
    - Body: `{ "title": str, "members": [user_id, ...] }`
  - `GET /api/boards/<id>/` – Board details including members and tasks
  - `PATCH /api/boards/<id>/` – Update title and/or members
    - Body examples: `{ "title": "New" }` or `{ "members": [1,2,3] }`
  - `DELETE /api/boards/<id>/` – Delete a board

- Tasks (`tasks_app.api.urls`)
  - `POST /api/tasks/` – Create task on a board (auth required)
    - Body: `{ "board": board_id, "title": str, "description": str?, "status": "to-do|in-progress|review|done", "priority": "low|medium|high", "assignee_id": user_id?, "reviewer_id": user_id?, "due_date": "YYYY-MM-DD"? }`
  - `GET /api/tasks/assigned-to-me/` – List tasks where you are assignee
  - `GET /api/tasks/reviewing/` – List tasks where you are reviewer
  - `PATCH /api/tasks/<id>/` – Update a task (board members only)
  - `DELETE /api/tasks/<id>/` – Delete a task (reviewer or board owner)
  - `GET /api/tasks/<id>/comments/` – List task comments
  - `POST /api/tasks/<id>/comments/` – Add a comment
    - Body: `{ "content": str }`
  - `DELETE /api/tasks/<id>/comments/<comment_id>/` – Delete a comment (author only)

Example Requests

Register:

```
curl -X POST http://127.0.0.1:8000/api/registration/ \
  -H "Content-Type: application/json" \
  -d '{
    "fullname": "Ada Lovelace",
    "email": "ada@example.com",
    "password": "secret123",
    "repeated_password": "secret123"
  }'
```

Login:

```
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "ada@example.com", "password": "secret123"}'
```

Create a board:

```
curl -X POST http://127.0.0.1:8000/api/boards/ \
  -H "Authorization: Token <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Engineering", "members": [2,3]}'
```

Create a task:

```
curl -X POST http://127.0.0.1:8000/api/tasks/ \
  -H "Authorization: Token <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "board": 1,
    "title": "Set up CI",
    "priority": "high",
    "assignee_id": 2,
    "reviewer_id": 1
  }'
```

Add a comment:

```
curl -X POST http://127.0.0.1:8000/api/tasks/42/comments/ \
  -H "Authorization: Token <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"content": "Looks good to me."}'
```

Project Structure

```
core/                # Django project (settings, URLs, WSGI/ASGI)
auth_app/            # Custom user model, auth API (login, register, email-check)
board_app/           # Boards, permissions, API (list/create/detail/update/delete)
tasks_app/           # Tasks, comments, permissions, API
manage.py            # Django management CLI
requirements.txt     # Python dependencies
```

Running Tests

```
python manage.py test
```

CORS

`CORS_ALLOWED_ORIGINS` allows `http://127.0.0.1:5500` by default (useful for a local frontend served via Live Server). Add your frontend origin(s) in `core/settings.py`.

Production Notes

- Set `DEBUG = False` and configure `ALLOWED_HOSTS`.
- Generate a secure `SECRET_KEY` and do not commit it.
- Switch `DATABASES` to a production database (PostgreSQL/MySQL).
- Consider HTTPS, CSRF and session security settings.
- Rotate/authenticate tokens and consider using JWT if preferred.
- Review and tighten CORS settings.

License

This project does not include a license file. If you plan to open source it, add a LICENSE to clarify usage rights.
