# SterlingShule — Local Development Setup

Multi-tenant Django 5.x school management system with a tropical dark-green theme,
CBC 8-level rubric assessments, attendance, fees, notices, analytics, and PDF report cards.

## Requirements

- Python 3.10+
- pip

## Quick start

```bash
# 1. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Install dependenc
pip install -r requirements.txt

# 3. Apply database migrations
python manage.py migrate

# 4. Create your global Django superuser (for /admin/)
python manage.py createsuperuser

# 5. Start the dev server
python manage.py runserver 0.0.0.0:8000
```

Open http://localhost:8000/

## Creating your first institution

1. Log into `http://localhost:8000/admin/` with the superuser you just created.
2. Under **Tenants → Institutions**, click "Add" and fill in the school name and a
   unique 6-digit `institution_key` (e.g. `123456`). Saving this auto-creates:
   - An ICT Admin user named `ictadmin_<key>` with a random password
   - Default Grade 1–6 class levels and 5 starter subjects
3. Under **Tenants → Institution bootstrap credentials** you'll find the temp
   password generated for that ICT Admin — copy it once.
4. Visit `http://localhost:8000/accounts/login/`, enter the institution key,
   the ICT Admin username, and the temp password.

From the ICT Admin account you can add teachers, students (CSV/XLSX upload
supported), assessments, fees, attendance and notices.

## Configuration

Environment variables (all optional):

| Variable        | Default      | Notes                                       |
|-----------------|--------------|---------------------------------------------|
| `SECRET_KEY`    | dev fallback | **Set this in production.**                 |
| `DEBUG`         | `True`       | Set `False` in production.                  |
| `ALLOWED_HOSTS` | `*`          | Comma-separated list.                       |
| `DB_ENGINE`     | `sqlite`     | Set `mysql` to use MySQL.                   |
| `DB_NAME`       | `sterling`   | MySQL database name.                        |
| `DB_USER`       | `root`       | MySQL user.                                 |
| `DB_PASSWORD`   | empty        | MySQL password.                             |
| `DB_HOST`       | `127.0.0.1`  | MySQL host.                                 |
| `DB_PORT`       | `3306`       | MySQL port.                                 |

For MySQL you must also `pip install mysqlclient` (uncomment in requirements.txt).

## Project structure

```
sterling_shule/
├── manage.py
├── requirements.txt
├── sterling_shule/             # Django project (settings, urls, wsgi)
├── apps/
│   ├── accounts/               # Custom User + roles + auth backend
│   ├── academics/              # Sessions, classes, streams, subjects, departments
│   ├── analytics/              # Dashboard + PDF analytics export
│   ├── assessments/            # Assessments + 8-level CBC rubric + marks entry
│   ├── attendance/             # Daily registers (mark-all-present)
│   ├── core/                   # Dashboard, theme toggle, shared template tags
│   ├── fees/                   # Fee structures, student liabilities, payments
│   ├── notices/                # Audience-scoped announcements
│   ├── reports/                # Student report-card PDFs
│   ├── students/               # Student CRUD + CSV/XLSX bulk upload
│   ├── teachers/               # Teacher CRUD + subject assignments
│   └── tenants/                # Institutions + multi-tenant signals
└── templates/                  # Base templates and shared partials
```

## Default roles

- `ICT_ADMIN` — full institution control
- `PRINCIPAL` — read/write for academic + admin modules
- `CLASS_TEACHER` — manage their class register, marks, notices to learners
- `SUBJECT_TEACHER` — enter marks for their subjects, mark attendance
- `STUDENT` / `PARENT` — read-only views (parent portal coming soon)

Tenant isolation is enforced by `request.institution` middleware on every view.
