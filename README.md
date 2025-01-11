
# 🎯 Habit Tracker - Transform Your Daily Routines

[![Django](https://img.shields.io/badge/Django-4.2+-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.0+-blueviolet.svg)](https://tailwindcss.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-6.0+-red.svg)](https://redis.io/)
[![Celery](https://img.shields.io/badge/Celery-5.2+-brightgreen.svg)](https://docs.celeryq.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🌐 Live Demo 
## (username:admin  password:myschool) (username:admin2  password:myschool)

Experience the Habit Tracker in action: [Habit Track App](https://habitapp.up.railway.app/)

<img src="habits/static/docs/images/habit21.png" width="600" alt="Habit Tracker Screenshot">

*Click [here](https://habitapp.up.railway.app/) to visit the live app*






## 🌟 Introduction

Welcome to Habit Tracker - your comprehensive solution for building and maintaining positive habits. Built with Django and modern technologies, this application combines powerful tracking capabilities with intuitive design to help you transform your daily routines into lasting positive changes.

Developed as part of my academic journey at IU International University, this project showcases both technical excellence and practical utility, helping users achieve their personal development goals through technology.

<p float="left">
  <img src="/habits/static/docs/images/hb1.jpg" width="400" alt="Habit Tracker "/>
  <img src="/habits/static/docs/images/hb2.jpg" width="400" alt="Habit Tracker"/>
</p>

## ✨ Features

### 📊 Intelligent Dashboard
- **Real-time Overview**
  - Dynamic habit status tracking
  - Visual progress indicators
  - Current and best streak displays
  - Priority-based organization
  - Daily/weekly completion rates

- **Interactive Statistics**
  - Date range analysis
  - Success rate calculations
  - Trend visualization
  - Performance metrics
  - Achievement highlights

<img src="/habits/static/docs/images/habit7.png" width="600" alt="Habit Tracker Dark Mode Dashboard">
### 📈 Advanced Analytics
- **Data Visualization**
  - Interactive Chart.js graphs
  - Success rate by weekday and monthly
  - Monthly trend analysis
  - Habit correlation insights
  - Custom date range reports

- **Performance Tracking**
  - Detailed completion statistics
  - Streak analytics
  - Time-based patterns
  - Category performance
  - Improvement suggestions
<img src="/habits/static/docs/images/habit8.png" width="600" alt="Habit Tracker Dark Mode Analytics">
### 🎯 Habit Management
- **Flexible Tracking**
  - Daily/weekly habit monitoring
  - Custom periodicity settings
  - Category organization
  - Progress bar and note

- **Smart Features**
  - Auto-detection of streaks
  - Intelligent reminders
  - Progress predictions
  - Achievement tracking
  - Habit insights


<img src="/habits/static/docs/images/habit9.png" width="600" alt="Habit Tracker Profile (Bio)">
## 🛠️ Technical Architecture

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

<img src="/habits/static/docs/images/habit10.png" width="600" alt="Habit Tracker Profile">

### Backend Framework
```python
# Core Technologies
- Django 4.2+
- Django REST Framework
- Celery 5.2+
- Channels 4.0+
- Redis 6.0+
- PostgreSQL 13+

# Key Components
- ASGI support
- WebSocket integration
- Task queue management
- Real-time updates
- Caching system
```
<img src="/habits/static/docs/images/habit11.png" width="600" alt="Habit Tracker Profile">

### Database Design
```postgresql
# Main Tables
- habits_habit
- habits_completion
- habits_category
- habits_streak
- habits_achievement
- auth_user

# Optimizations
- Indexed queries
- Materialized views
- Query optimization
- Data partitioning
```

<img src="/habits/static/docs/images/habit2.png" width="600" alt="Habit Tracker Analytics">

### Frontend Stack
```javascript
# Core Technologies
- Tailwind CSS 3.0
- Alpine.js 3.0
- Chart.js 4.0
- HTML5/CSS3

# Features
- Responsive design
- Dark/Light modes
- Real-time updates
```
<img src="/habits/static/docs/images/habit3.png" width="600" alt="Habit Tracker Analytics">

## 📦 Installation

### Prerequisites
```bash
# Mac Installation
brew install python@3.11 postgresql redis node

# Linux Installation
sudo apt update
sudo apt install python3.11 postgresql redis-server nodejs npm
```

### Environment Setup
```bash
# Clone and Setup
git clone https://github.com/frankkode/masabo-frank-habit-track-2024.git
cd habitapp

# Virtual Environment
python3 -m venv env
source env/bin/activate  # Linux/Mac
.\env\Scripts\activate   # Windows

# Dependencies
pip install -r requirements.txt
```

### Database Configuration
```bash
# PostgreSQL Setup
python3 manage.py makemigrations

python3 manage.py migrate

# Redis Configuration
redis-server
```

### Environment Variables
```env
# Core Settings
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=your-domain.com,localhost

# Database URLs
DATABASE_URL=postgresql://user:pass@localhost:5432/habit_tracker
REDIS_URL=redis://localhost:6379/0

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your@email.com
EMAIL_HOST_PASSWORD=your-app-password
```

<img src="/habits/static/docs/images/habit4.png" width="600" alt="Habit Tracker Create Habit">

```# Cloudinary Settings
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```
## 🚀 API Reference

### Authentication Endpoints
```http
POST /api/auth/login/
POST /api/auth/register/
POST /api/auth/refresh/
```
<img src="/habits/static/docs/images/habit12.png" width="600" alt="Habit Tracker Notification">

### Habit Management
```http
GET    /api/habits/
POST   /api/habits/
GET    /api/habits/{id}/
PUT    /api/habits/{id}/
DELETE /api/habits/{id}/
POST   /api/habits/{id}/complete/
```
<img src="/habits/static/docs/images/habit14.png" width="600" alt="Habit Tracker change password">

### Analytics Endpoints
```http
GET /api/analytics/overview/
GET /api/analytics/trends/
GET /api/analytics/streaks/
```

## Export Data

<img src="/habits/static/docs/images/habit16.png" width="600" alt="Habit Tracker export">

## Delete a habit
<img src="/habits/static/docs/images/habit6.png" width="600" alt="Habit Tracker testing">

## 🧪 Testing

<img src="/habits/static/docs/images/habit13.png" width="600" alt="Habit Tracker testing">

```bash
# Run Tests
python manage.py pytest

# Specific Tests
pytest habits/tests/test_views.py
pytest habits/tests/test_models.py

# Coverage
pytest --cov=habits --cov-report=html
```

### Habit Tracker Login

<img src="/habits/static/docs/images/habit18.png" width="600" alt="Habit Tracker Login">

## 👥 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 Code Standards

```python
# Python Style Guide
- PEP 8 compliance
- Type hints usage
- Docstring documentation
- Unit test coverage
- Clean code principles
```
## Administration
To access administration dashboard just write your domain then /admin
ex: https://habity.up.railway.app/admin

## Mobile responsiviness (small screens)
<p float="left">
  <img src="/habits/static/docs/images/1.jpg" width="400" alt="Habit Tracker Mobile 1"/>
  <img src="/habits/static/docs/images/2.jpg" width="400" alt="Habit Tracker Mobile 2"/>
</p>
<p float="left">
  <img src="/habits/static/docs/images/3.jpg" width="400" alt="Habit Tracker Mobile 3"/>
  <img src="/habits/static/docs/images/4.jpg" width="400" alt="Habit Tracker Mobile 4"/>
</p>

## 🌟 Conclusion

Habit Tracker represents the intersection of technology and personal development. Built with modern tools and focused on user experience, it provides a robust platform for habit formation and tracking. Whether you're a developer looking to contribute or a user seeking to improve your life, this application offers the features and support needed for successful habit building.


## Project Database schema

<img src="/habits/static/docs/images/schema.png" width="900" alt="Habit Tracker database schema"/>


## 🙏 Acknowledgments

- Django Community
- Tailwind CSS Team
- Chart.js Contributors
- International University (IU)
- Open Source Community



---


Developed with 💪 by Frank Masabo

For questions or support contact me: frank.masabo@iu-study.org

Note:This project was created as my school assignment (IU).
