from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from src.services.health_service import HealthService


class HealthCheckController(APIView):
    """
    Health check controller to verify backend availability.
    Endpoint: GET /health
    Expected Response: {"status": "ok"}
    """
    # Exclude from CSRF requirements for basic monitoring
    authentication_classes = []
    permission_classes = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.health_service = HealthService()

    def get(self, request, *args, **kwargs):
        """Handle GET /health check request."""
        payload = self.health_service.check_health()
        return Response(payload, status=status.HTTP_200_OK)
