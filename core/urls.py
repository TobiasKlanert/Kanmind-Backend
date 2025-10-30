"""
Root URL configuration for the Kanmind project.

This module defines the top-level URL routing for the entire project.
URLs are organized by app and mounted at appropriate paths:

Main endpoints:
- /admin/           : Django admin interface
- /api/            : Authentication endpoints (login, register, etc.)
- /api/boards/     : Board management endpoints
- /api/tasks/      : Task management endpoints

For detailed URL patterns within each app, see their respective urls.py files:
- auth_app.api.urls
- board_app.api.urls
- tasks_app.api.urls
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django admin interface
    path('admin/', admin.site.urls),

    # Authentication endpoints (login, register, etc.)
    path('api/', include('auth_app.api.urls')),

    # Board management endpoints (CRUD operations for boards)
    path('api/boards/', include('board_app.api.urls')),

    # Task management endpoints (CRUD operations for tasks)
    path('api/tasks/', include('tasks_app.api.urls')),
]
