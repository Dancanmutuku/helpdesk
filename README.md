# IT HelpDesk System — Setup Guide

## 📋 Requirements

- Python 3.10+
- PostgreSQL 13+
- pip

---

## 🚀 Step-by-Step Setup

### Step 1: Create the PostgreSQL Database

```sql
-- Open psql and run:
CREATE DATABASE it_db;
CREATE USER helpdesk_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE it_db TO helpdesk_user;
```

### Step 2: Install Python Dependencies

```bash
cd helpdesk
pip install -r requirements.txt
```

### Step 3: Configure Database Settings

Edit `config/settings.py` and update the DATABASES block:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'it_db',
        'USER': 'helpdesk_user',       # or 'postgres'
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Step 4: Run Migrations

```bash
python manage.py makemigrations accounts tickets knowledge dashboard
python manage.py migrate
```

### Step 5: Seed Initial Data

```bash
python manage.py seed_data
```

This creates:
- Departments and categories
- 3 demo accounts (admin, agent, user)
- Sample knowledge base articles
- Canned responses

**Demo Credentials:**
| Role | Username | Password |
|------|----------|----------|
| IT Manager / Admin | `admin` | `Admin@123` |
| IT Support Agent | `agent1` | `Agent@123` |
| End User | `user1` | `User@123` |

### Step 6: Collect Static Files (Production)

```bash
python manage.py collectstatic
```

### Step 7: Start the Server

```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000**

---

## 📁 Project Structure

```
helpdesk/
├── config/                  # Django project settings & URLs
│   ├── settings.py
│   └── urls.py
├── accounts/                # User auth, roles, departments
│   ├── models.py            # Custom User, Department
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── tickets/                 # Core ticket management
│   ├── models.py            # Ticket, Reply, Attachment, History
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── knowledge/               # Knowledge base & articles
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── dashboard/               # Analytics & dashboards
│   ├── views.py
│   └── urls.py
├── templates/               # Django HTML templates
│   ├── base/base.html       # Main layout with sidebar
│   ├── accounts/            # Login, register, profile
│   ├── tickets/             # List, detail, submit, queue
│   ├── knowledge/           # KB home, article
│   └── dashboard/           # Dashboard, reports
├── static/
│   ├── css/main.css         # Complete design system
│   └── js/main.js           # Interactions & SLA timers
└── requirements.txt
```

---

## 👥 User Roles

| Role | Capabilities |
|------|-------------|
| **End User** | Submit/track own tickets, KB access, rate support |
| **IT Agent** | Manage all tickets, reply, internal notes, assign |
| **IT Manager** | Full dashboard, agent management, reports, KB management |

---

## 🎫 Key Features

- **Ticket Management** — Auto-generated IDs, SLA tracking, priorities, categories
- **SLA Timers** — Real-time countdown timers on tickets, overdue warnings
- **Threaded Replies** — Internal notes (agent-only), user replies, attachments
- **Ticket History** — Full audit log of all changes
- **CSAT Ratings** — 1-5 star feedback on resolved tickets
- **Knowledge Base** — Searchable articles, helpfulness voting
- **Role-based Dashboards** — Different views for users, agents, managers
- **Canned Responses** — Quick reply templates for agents
- **Auto-Assignment** — Category-based auto-routing of tickets
- **Reports** — Monthly volume trends, agent performance, CSAT

---

## ⚙️ Configuration

### SLA Response Times (in hours)
Edit `config/settings.py`:
```python
SLA_RESPONSE_TIMES = {
    'low': 48,
    'medium': 24,
    'high': 8,
    'critical': 2,
}
```

### Email Notifications
Configure SMTP in `settings.py`:
```python
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your@email.com'
EMAIL_HOST_PASSWORD = 'your_app_password'
```

---

## 🔧 Django Admin Panel

Access at `/admin/` with the admin account.

From the admin panel you can:
- Manage all users, agents, departments
- Configure ticket categories and auto-assignments
- Create/edit canned responses
- View full audit logs
- Export data

---

## 📝 Notes

- Change `SECRET_KEY` in `settings.py` before production
- Set `DEBUG = False` in production
- Configure `ALLOWED_HOSTS` for your domain
- Use environment variables for sensitive settings
