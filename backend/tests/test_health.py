import unittest
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from src.services.health_service import HealthService


class HealthServiceUnitTest(unittest.TestCase):
    """
    Unit tests for the HealthService business layer.
    Runs in isolation without starting a web server (satisfies R17 & R27).
    """

    def setUp(self):
        self.service = HealthService()

    def test_check_health_returns_ok_status(self):
        result = self.service.check_health()
        self.assertIsInstance(result, dict)
        self.assertEqual(result, {"status": "ok"})


class HealthControllerIntegrationTest(TestCase):
    """
    Integration tests for the HTTP API layer (GET /health).
    """

    def setUp(self):
        self.client = APIClient()

    def test_health_endpoint_returns_200_and_ok_json(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_health_endpoint_trailing_slash_returns_200(self):
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"status": "ok"})
