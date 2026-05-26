# TIKITAKA Django Application

TIKITAKA is an online academy platform built with Django. It separates student
and teacher roles and includes course management, lesson playback, reviews,
community boards, social login, and 1:1 chat.

## Main Features

- Custom user model with student/teacher roles
- Course and lesson management
- Student and teacher dashboards
- Reviews and community board
- Django Channels based chat structure
- MySQL/Aurora connection with writer/reader endpoints
- Optional S3 media storage through django-storages

## Environment Values To Fill

Copy `.env.example` to `.env` and fill these values outside Git:

- `DJANGO_SECRET_KEY`
- `DB_PASSWORD`
- `DB_MASTER_HOST`
- `DB_SLAVE_HOST`
- `AWS_STORAGE_BUCKET_NAME`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`

## Local Setup

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py runserver
```

## Portfolio Note

This repository is prepared for portfolio review. Local virtual environments,
uploaded media, and real secret values should not be committed.
