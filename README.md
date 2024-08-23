# Multi-User Management System Documentation

This document provides an overview of the Multi-User Management System, detailing its structure, functionality, and how to interact with its various components. The system is built using Django and Django REST Framework, with additional features for task management, user authentication, and real-time notifications via WebSockets using Django Channels.

## Overview

The Multi-User Management System is designed to manage users and tasks within an organization. It supports user registration, authentication, task creation, assignment, and real-time notifications for task updates. The system is divided into two main apps: `users` and `tasks`. The `users` app handles user-related functionalities, including registration, login, and admin functionalities. The `tasks` app manages tasks, including creation, assignment, tagging, and commenting. Real-time notifications are implemented using Django Channels for updates on task assignments and changes.

## Setup

### Requirements

- Django 4.0.5
- Django REST Framework
- Django Channels
- djangorestframework-simplejwt for JWT authentication
- drf-yasg for API documentation
- channels_redis for WebSocket communication

### Installation

1. Clone the repository.
2. Install the required packages using `pip install -r requirements.txt`.
3. Set up your database in `settings.py`.
4. Run migrations with `python manage.py migrate`.
5. Start the server with `python manage.py runserver`.
6. create superuser with `python manage.py createsuperuser`.
7. For WebSocket support, run Daphne or Uvicorn with ASGI support: `daphne -u asgi:application` or `uvicorn core.asgi:application`.
8. pip install -r requirements.txt and run `python manage.py runserver`
9. POSTMAN DOCS LINK: <https://documenter.getpostman.com/view/31639947/2sAXjDfbVg>

## Users App

### User Registration and Authentication

The `users` app provides endpoints for user registration, login, and logout. It uses JWT for authentication.

#### Endpoints

- **Register**: `POST /api/register/` - Registers a new user.
- **Login**: `POST /api/login/` - Authenticates a user and returns JWT tokens.
- **Logout**: `POST /api/logout/` - Logs out a user by blacklisting the refresh token.
- **Admin Registration**: `POST /api/admin-register/` - Registers a new admin user (requires superuser permissions).

### Models

- **User**: Custom user model with email as the username field.

### Permissions

- Custom permissions are defined in `permissions.py` to restrict access based on user roles (admin, staff, authenticated).

## Tasks App

### Task Management

The `tasks` app allows users to create, update, and delete tasks. It supports tagging tasks and adding comments.

#### Endpoints

- **List/Create Tasks**: `GET/POST /api/tasks/` - Lists all tasks or creates a new task.
- **Task Detail**: `GET/PUT/DELETE /api/tasks/<int:pk>/` - Retrieves, updates, or deletes a specific task.
- **Add Tags to Task**: `PATCH /api/tag/<int:pk>/` - Adds tags to a task.
- **List/Create Comments**: `GET/POST /api/tasks/<int:task_id>/comments/` - Lists comments on a task or adds a new comment.
- **Comment Detail**: `GET/PUT/DELETE /api/comments/<int:pk>/` - Retrieves, updates, or deletes a specific comment.

### Models

- **Task**: Represents a task with fields for title, description, due date, status, assigned user, and tags.
- **Tag**: Represents a tag that can be associated with tasks.
- **Comment**: Represents a comment on a task.

### Real-time Notifications

The system uses Django Channels to send real-time notifications to users about task updates. Notifications are sent when a task is assigned to a user or when a task's status changes.

#### WebSocket Connection

- Connect to `ws/notifications/<int:user_id>/` to receive notifications.

## API Documentation

API documentation is available via POSTMAN <https://documenter.getpostman.com/view/31639947/2sAXjDfbVg>

## Authentication

The system uses JWT for authentication. Obtain tokens via the login endpoint and include them in the `Authorization` header for authenticated requests.
