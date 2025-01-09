# Habit Tracker
A comprehensive Django-based habit tracking application that helps users build and maintain positive habits through daily and weekly tracking, analytics, and motivational features.

![Dashboard Preview](docs/images/dashboard.png)

## ✨ Key Features

### 📊 Smart Dashboard
- Real-time habit overview
- Success rate statistics
- Current streaks display
- Quick-action completion buttons
- Progress indicators

### 📈 Advanced Analytics
- Detailed completion trends
- Success rate by weekday
- Streak history tracking
- Performance insights
- Custom date range analysis

### 🎯 Flexible Habit Management
- Daily/Weekly habit tracking
- Custom periodicity settings
- Habit categorization
- Priority levels
- Notes and reflections

### 🏆 Achievement System
- Milestone tracking
- Streak achievements
- Progress badges
- Achievement history
- Motivational notifications

### 📱 Modern UI/UX
- Responsive design
- Dark/Light mode
- Touch-friendly interface
- Intuitive navigation
- Accessibility support

### 🔔 Smart Notifications
- Email reminders
- Achievement alerts
- Streak notifications
- Custom scheduling
- Notification preferences

## 🛠️ Technology Stack

### Backend
- Python 3.11+
- Django 4.2+
- Django REST Framework
- Celery 5.2+
- Redis 6.0+
- PostgreSQL 13+

### Frontend
- Tailwind CSS 3.0
- Alpine.js 3.0
- Chart.js 4.0
- HTML5/CSS3

### DevOps
- Docker
- Git
- GitHub Actions

## 📦 Installation

### Prerequisites
```bash
# Install Homebrew (Mac)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.11 postgresql redis node
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
```

## Installation

### Setup Steps
```bash
# Clone the repository
git clone https://github.com/frankkode/masabo-frank-habit-track-2024.git

cd habitapp 

# Create and activate virtual environment
python3 -m venv env
source env/bin/activate  # On Mac/Linux
.\env\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run migrations
python3 manage.py migrate

# Create superuser
python3 manage.py createsuperuser

# Build CSS
python3 manage.py tailwind install
python3 manage.py tailwind build
python3 manage.py collectstatic
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
python3 manage.py runserver

# Run tests
python3 manage.py pytest
```
## Configuration (in settings)
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgres://user:pass@localhost:5432/habit_tracker
REDIS_URL=redis://localhost:6379/0
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your@email.com
EMAIL_HOST_PASSWORD=your-app-password
## 🚀 API Endpoints

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
- **Charts**: Visual representation of progress using Chart.js

## Development

### Running Tests
```bash
# Run all tests
python3 manage.py pytest

# Run specific test file
python3 manage.py pytest habits/tests/test_views.py
```

### Code Style
The project follows PEP 8 style guide for Python code. Use `flake8` for linting:
```bash
flake8 .
```

## 🧪 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

* Django Documentation
* Tailwind CSS
* Chart.js

---
Built with 💪 for better habits and personal growth.

Note:This project was created as my school assignment (IU).