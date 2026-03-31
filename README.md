# AnnotatePro — Django Data Annotation Platform

A two-sided data annotation platform where companies upload files (images or PDFs) with questions, and annotators review and respond to them.

## Features

- **Company Portal**: Upload image/PDF to Cloudinary, write a question, choose answer type (Yes/No or Free Text)
- **Annotator Portal**: Login, see the latest unanswered task, submit answers (big Yes/No buttons or free text)
- **Admin Panel**: Full Django admin for managing users, tasks, and annotations
- **Role-based access control**: Company and Annotator roles with route protection
- **Tailwind CSS UI**: Clean, responsive design via Tailwind CDN

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 4.2 |
| File storage | Cloudinary |
| Database | PostgreSQL (prod) / SQLite (dev) |
| Static files | WhiteNoise |
| WSGI server | Gunicorn |
| Config | python-decouple |
| Deployment | Railway.app |

## Local Development

### 1. Clone and install dependencies

```bash
git clone <repo-url>
cd annotation-platform
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your values
```

Required variables:

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` for development, `False` for production |
| `DATABASE_URL` | Database URL (default: SQLite) |
| `CLOUDINARY_URL` | Cloudinary URL (`cloudinary://key:secret@cloud`) |

### 3. Run migrations

```bash
python manage.py makemigrations core
python manage.py migrate
```

### 4. Create users

```bash
python manage.py createsuperuser
```

Then in Django admin (`/admin/`), create:
- At least one **Company** user (role = company)
- At least one **Annotator** user (role = annotator)

### 5. Start the server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` to see the login page.

## User Roles

### Company Users (`role = 'company'`)
- `/company/upload/` — Upload a file and create a task
- `/company/results/` — View all tasks and annotator responses

### Annotator Users (`role = 'annotator'`)
- `/annotator/` — View the latest unanswered task and submit a response
- Tasks are served in LIFO order; already-answered tasks are skipped

## Cloudinary Setup

1. Create a free account at [cloudinary.com](https://cloudinary.com)
2. From the dashboard, copy your **Cloud URL** (format: `cloudinary://api_key:api_secret@cloud_name`)
3. Set `CLOUDINARY_URL` in your `.env` file

## Deployment on Railway

1. Push to GitHub
2. Create a new Railway project and connect your repo
3. Add a PostgreSQL service
4. Set environment variables:
   - `SECRET_KEY` — a strong random string
   - `DEBUG` — `False`
   - `DATABASE_URL` — auto-provided by Railway PostgreSQL
   - `CLOUDINARY_URL` — your Cloudinary URL
5. Railway will detect the `Procfile` and deploy automatically

## Project Structure

```
annotation-platform/
├── manage.py
├── requirements.txt
├── Procfile
├── runtime.txt
├── .env.example
├── README.md
├── annotation_platform/
│   ├── settings.py      # Django settings (decouple + dj-database-url)
│   ├── urls.py          # Root URL config
│   └── wsgi.py
└── core/
    ├── models.py        # User, Task, Annotation models
    ├── views.py         # All views (login, upload, results, dashboard)
    ├── urls.py          # App URL patterns
    ├── forms.py         # LoginForm, TaskUploadForm, AnnotationForm
    ├── decorators.py    # role_required decorator
    ├── admin.py         # Django admin registrations
    └── templates/
        ├── base.html    # Tailwind CDN layout + nav + flash messages
        ├── login.html   # Centered login card
        ├── company/
        │   ├── upload.html   # File upload form with Cloudinary
        │   └── results.html  # Results table with all annotations
        └── annotator/
            └── dashboard.html  # Task viewer + Yes/No buttons or textarea
```

## License

MIT
