"""
URL configuration for the authentication API endpoints.

This module exposes the following API routes (used by the auth_app):
- registration/  : User registration endpoint (RegistrationView)
- login/         : Login endpoint (CustomLoginView) — returns auth token/session
- email-check/   : Endpoint to verify if an email is already registered (EmailCheckView)
"""

from django.urls import path
from .views import RegistrationView, CustomLoginView, EmailCheckView

urlpatterns = [
    # POST: create a new user account. Uses RegistrationView.as_view().
    path('registration/', RegistrationView.as_view(), name='registration'),

    # POST: authenticate user credentials and return a token.
    path('login/', CustomLoginView.as_view(), name='login'),

    # GET: check whether an email is available or already taken.
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
]