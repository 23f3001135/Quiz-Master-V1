# Quiz Master

A comprehensive web application for creating, managing and taking quizzes. This project was developed as part of the Modern Application Development I course (BSCS2003P) at IIT Madras.

## Project Overview

Quiz Master is a Flask-based web application that allows administrators to create subjects, chapters, quizzes, and questions, while users can take quizzes and track their scores. The application implements role-based access control, secure authentication, and a responsive user interface.

## Features

### User Features
- User registration and authentication
- Browse available quizzes by subject or through search
- Take quizzes within scheduled time periods
- Receive immediate feedback on quiz submissions
- View quiz history and performance statistics

### Admin Features
- Comprehensive dashboard for content management
- Create and manage subjects, chapters, quizzes, and questions
- Set quiz schedules and durations
- View all registered users
- Search functionality for users, subjects, quizzes, and questions

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML, CSS, Bootstrap
- **Authentication**: Session-based authentication with password hashing (using flask-session and werkzeug)

## Project Structure
quiz_master/ 
├── models.py # Database models 
├── routes.py # Application routes and logic 
├── app.py    # Main application file 
└─ templates/ # HTML templates 
  │ 
  ├── admin/  # Admin dashboard templates 
  │ 
  ├── user_dashboard/ # User dashboard templates 
  │ 
  └── static/ # Static files

## How to run the Project

1. first create venv, "python -m venv .venv" (or python3 -m venv .venv)
2. Activate the venv, with "source .venv/bin/activate"
3. Install libraries with, "pip install -r requirements.txt"
4. "python app.py" or "flask run"