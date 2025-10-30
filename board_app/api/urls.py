"""
URL configuration for the board app API endpoints.

This module defines the URL patterns for board-related views:
- List/Create boards (BoardListCreateView)
- Retrieve/Update/Delete specific boards (BoardDetailView)

The URLs are included under the 'api/boards/' prefix as defined in the root URLconf.
"""

from django.urls import path
from .views import BoardListCreateView, BoardDetailView

urlpatterns = [
    # API endpoint for listing all boards and creating new ones
    # GET: Returns list of boards the user has access to
    # POST: Creates a new board
    path('', BoardListCreateView.as_view(), name='boards'),

    # API endpoint for specific board operations
    # GET: Returns detailed board information
    # PATCH: Updates board details
    # DELETE: Removes the board
    # The <int:pk> parameter captures the board's ID from the URL
    path('<int:pk>/', BoardDetailView.as_view(), name='board-detail')
]
