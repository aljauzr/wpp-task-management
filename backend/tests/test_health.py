import unittest

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from src.services.health_service import HealthService


class HealthServiceUnitTest(unittest.TestCase):
    def test_check_health_returns_ok_status(self):
        assert HealthService().check_health() == {"status": "ok"}


class HealthControllerIntegrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_health_endpoint_returns_200_and_ok_json(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"status": "ok"})
