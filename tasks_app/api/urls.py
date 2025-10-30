"""
URL configuration for the tasks app API endpoints.

This module defines the URL patterns for task-related views.
All URLs are mounted under 'api/tasks/' as defined in the root URLconf.

Available endpoints:
- POST /                              : Create new tasks
- GET  /assigned-to-me/               : List tasks assigned to current user
- GET  /reviewing/                    : List tasks where user is reviewer
- GET/PATCH/DELETE /<id>/             : Task detail operations
- GET/POST /<id>/comments/            : List/create task comments
- GET/PATCH/DELETE /<id>/comments/<id>: Comment detail operations
"""

from django.urls import path
from .views import (
    CreateTaskView,
    AssignedTaskListView,
    ReviewingTaskListView,
    TaskDetailView,
    TaskCommentView,
    TaskCommentDetailView,
)

urlpatterns = [
    # Create new tasks
    # POST: Creates a task and assigns it to a board
    path('', CreateTaskView.as_view(), name='create-task'),

    # List tasks assigned to the current user
    # GET: Returns tasks where user is the assignee
    path('assigned-to-me/', AssignedTaskListView.as_view(), name='assigned-tasks'),

    # List tasks where current user is reviewer
    # GET: Returns tasks where user is set as reviewer
    path('reviewing/', ReviewingTaskListView.as_view(), name='reviewing-tasks'),

    # Task detail operations
    # GET: Retrieve task details
    # PATCH: Update task fields
    # DELETE: Remove task (requires reviewer/owner permission)
    path('<int:pk>/', TaskDetailView.as_view(), name='task-detail'),

    # Task comments list/create
    # GET: List all comments for a task
    # POST: Add a new comment to the task
    path('<int:pk>/comments/', TaskCommentView.as_view(), name='task-comments'),

    # Comment detail operations
    # GET: Retrieve specific comment
    # DELETE: Remove comment (requires author permission)
    path('<int:pk>/comments/<int:comment_pk>/', TaskCommentDetailView.as_view(), 
         name='task-comment-detail'),
]
