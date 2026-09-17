"""
URL configuration for task-management backend service.
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from src.controllers.health_controller import HealthCheckController
from src.controllers.board_viewset import BoardViewSet
from src.controllers.task_viewset import TaskViewSet

# Create router and register ViewSets
router = DefaultRouter()
router.register(r'boards', BoardViewSet, basename='board')

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),

    # Minimal health check endpoint (as specified in init brief: GET /health -> {"status": "ok"})
    path('health', HealthCheckController.as_view(), name='health-check-short'),
    path('health/', HealthCheckController.as_view(), name='health-check'),

    # API endpoints
    path('api/', include(router.urls)),

    # Task endpoints (custom routing for board-scoped and direct task access)
    path('api/boards/<int:board_id>/tasks/', TaskViewSet.as_view({'get': 'list_tasks_by_board', 'post': 'create_task_on_board'}), name='board-tasks'),
    path('api/tasks/<int:pk>/', TaskViewSet.as_view({'patch': 'partial_update', 'delete': 'destroy'}), name='task-detail'),
]
