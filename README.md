# Habit Tracker
A comprehensive Django-based habit tracking application that helps users build and maintain positive habits through daily and weekly tracking, analytics, and motivational features.

## Features
- 📊 Dashboard with habit overview and statistics
- 📈 Detailed analytics and progress tracking
- 🎯 Daily and weekly habit tracking
- 🏆 Streak tracking and milestone achievements
- 📱 Responsive design for mobile and desktop
- 🌙 Dark mode support
- 📧 Email notifications for reminders
- 📊 Visual progress with charts
- 🔒 User authentication and personal habits

## Tech Stack
- Django 4.2+
- Python 3.11
- PostgreSQL
- Redis (for Celery)
- Celery (background tasks)
- Tailwind CSS
- Chart.js
- Django REST Framework

## Project Structure
```
habit-track-2024/
├── habitapp/
│   ├── habits/
│   │   ├── migrations/
│   │   ├── templatetags/
│   │   │   ├── __init__.py
│   │   │   └── habit_tags.py
│   │   ├── templates/
│   │   │   └── habits/
│   │   │       ├── analytics.html
│   │   │       ├── dashboard.html
│   │   │       ├── habit_confirm_delete.html
│   │   │       ├── habit_detail.html
│   │   │       ├── habit_form.html
│   │   │       ├── habit_form_update.html
│   │   │       └── notifications.html
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   ├── test_models.py
│   │   │   ├── test_tasks.py
│   │   │   └── test_views.py
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── analytics.py
│   │   ├── api.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── streak_utils.py
│   │   ├── tasks.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css
│   │   ├── js/
│   │   │   └── charts.js
│   │   └── images/
│   ├── templates/
│   │   ├── base.html
│   │   ├── registration/
│   │   │   ├── login.html
│   │   │   └── signup.html
│   │   └── includes/
│   │       ├── header.html
│   │       └── footer.html
│   ├── habitapp/
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── celery.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── manage.py
│   ├── requirements.txt
│   └── README.md
├── .env
├── .gitignore
└── docker-compose.yml
```

## Installation

### Prerequisites
- Python 3.11+
- Node.js and npm
- Redis server
- PostgreSQL

### Setup Steps
```bash
# Clone the repository
git clone https://github.com/yourusername/habit-tracker.git
cd habit-tracker

# Create and activate virtual environment
python -m venv env
source env/bin/activate  # On Mac/Linux
.\env\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Install frontend dependencies
npm install

# Build CSS
python manage.py tailwind install
python manage.py tailwind build
```

### Running the Application

```bash
# Start Redis server (required for Celery)
brew services start redis

# Start Celery worker
celery -A habit_tracker worker -l info

# Start Celery beat for periodic tasks
celery -A habit_tracker beat -l info

# Run development server
python manage.py runserver

# Run tests
python manage.py pytest
```

## API Endpoints

* `GET /api/habits/` - List all habits
* `POST /api/habits/` - Create new habit
* `GET /api/habits/{id}/` - Get habit details
* `PUT /api/habits/{id}/` - Update habit
* `DELETE /api/habits/{id}/` - Delete habit
* `POST /api/habits/{id}/complete/` - Complete habit

## Key Components

### Models
- **Habit**: Core model for habit definition and tracking
- **HabitCompletion**: Records individual habit completions
- **Notification**: Handles user notifications and achievements

### Features Implementation
- **Streak Tracking**: Automated calculation of daily/weekly streaks
- **Analytics**: Detailed insights into habit performance
- **Dark Mode**: System-wide theme support
- **Email Notifications**: Automated reminders and achievement notifications
- **Charts**: Visual representation of progress using Chart.js

## Development

### Running Tests
```bash
# Run all tests
python manage.py pytest

# Run specific test file
python manage.py pytest habits/tests/test_views.py
```

### Code Style
The project follows PEP 8 style guide for Python code. Use `flake8` for linting:
```bash
flake8 .
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

* Django Documentation
* Tailwind CSS
* Chart.js

---
Built with 💪 for better habits and personal growth.