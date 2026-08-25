# SIH Environmental Education Platform Backend

This repository contains a simple, clean Django REST backend for the SIH environmental education and eco-action MVP. It follows the technical specification closely while keeping the implementation straightforward and easy to debug.

## Stack

- Python 3
- Django
- Django REST Framework
- JWT via `djangorestframework-simplejwt`
- PostgreSQL-ready database configuration with SQLite fallback for quick local startup
- drf-spectacular for OpenAPI docs

## Core MVP Features

- Custom user model with `STUDENT` and `ADMIN` roles
- Student and admin onboarding
- Institutions with state and district hierarchy
- Activity list, activity of the day, submissions, and manual verification
- Eco points, streaks, badges, and leaderboard APIs
- Quiz submission and score-based point awarding
- Time-bound campaigns with proof submission and admin verification
- Student dashboard and admin analytics endpoints
- Django admin for managing master data

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and update values.
4. Apply migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

5. Seed demo data:

```bash
python manage.py seed_demo
```

6. Create a superuser if needed:

```bash
python manage.py createsuperuser
```

7. Start the server:

```bash
python manage.py runserver
```

## API Docs

- Schema: `/api/schema/`
- Swagger UI: `/api/docs/`

## Demo Credentials

After running `seed_demo`:

- Student: `student@example.com` / `Student@123`
- Admin: `teacher@example.com` / `Teacher@123`

## Important Endpoints

- `POST /api/auth/register/`
- `POST /api/auth/token/`
- `GET /api/auth/profile/`
- `GET /api/institutions/`
- `GET /api/activities/`
- `GET /api/activities/daily/`
- `POST /api/activities/{id}/submit/`
- `POST /api/activities/submissions/{id}/review/`
- `GET /api/quizzes/`
- `POST /api/quizzes/{id}/submit/`
- `GET /api/campaigns/`
- `POST /api/campaigns/{id}/submit/`
- `POST /api/campaigns/submissions/{id}/review/`
- `GET /api/dashboard/student/`
- `GET /api/dashboard/admin/`
- `GET /api/dashboard/leaderboard/`

## Notes

- PostgreSQL is the intended production database from the spec. The settings keep a SQLite fallback so the project can boot quickly without extra setup.
- Media uploads are stored locally under `media/`.
- Point awards are tracked transactionally to prevent duplicate rewards.
- Quiz answers are never exposed through the student-facing API.
