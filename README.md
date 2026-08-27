# ProjectFlow

A project management application built with Django 6.1. Manage projects, tasks, issues, sprints, and team collaboration with a modern dark/light themed UI.

## Features

- **Projects** - Create and manage projects with team members, roles, and status tracking
- **Tasks** - Kanban board for task management with drag-and-drop, priorities, and tags
- **Issues** - Bug/issue tracking with severity, steps to reproduce, and resolution fields
- **Sprints** - Sprint planning and progress tracking
- **Calendar** - Calendar view for task scheduling
- **Activity Feed** - Track all project activity across users
- **Notifications** - Real-time notification system
- **Theming** - Dark, light, and system theme support

## Tech Stack

- **Backend:** Django 6.1, Python
- **Database:** SQLite
- **Frontend:** Vanilla JS, Material Icons, Inter font
- **Auth:** Custom user model with email-based login

## Project Structure

```
ProjectManagement/
├── config/             # Django settings, URLs, WSGI
├── core/               # Dashboard, shared utilities, context processors
├── accounts/           # Custom user model, auth views
├── projects/           # Project CRUD, memberships, roles
├── tasks/              # Task management, Kanban boards, tags
├── issues/             # Issue/bug tracking, comments, Kanban
├── sprints/            # Sprint planning and tracking
├── calendar_view/      # Calendar interface
├── activity/           # Activity logging and feed
├── notifications/      # Notification system
├── templates/          # Global templates
├── static/             # CSS, JS, images
├── manage.py
└── seed_data.py        # Sample data for development
```

## Setup

### Prerequisites

- Python 3.10+

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd ProjectManagement
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

3. Install dependencies:

```bash
pip install django
```

4. Run migrations:

```bash
python manage.py migrate
```

5. Create a superuser:

```bash
python manage.py createsuperuser
```

6. (Optional) Load sample data:

```bash
python manage.py shell < seed_data.py
```

7. Run the development server:

```bash
python manage.py runserver
```

Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) to access the app.

## License

This project is for internal use.
