"""
URL configuration for task-management backend service.
"""

from django.contrib import admin
from django.urls import path
from src.controllers.health_controller import HealthCheckController

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),

    # Minimal health check endpoint (as specified in init brief: GET /health -> {"status": "ok"})
    path('health', HealthCheckController.as_view(), name='health-check-short'),
    path('health/', HealthCheckController.as_view(), name='health-check'),
]
