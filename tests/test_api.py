import unittest
import sys
import os

# Ensure the app folder is in the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../app")))

from fastapi.testclient import TestClient
from main import app

class TestLiturgicalDayAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_root_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertIn("docs_url", data)

    def test_liturgical_day_today(self):
        response = self.client.get("/liturgical-day")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("date", data)
        self.assertIn("main_day", data)
        self.assertIn("commemorations", data)

    def test_liturgical_day_specific_date(self):
        # Pentecost 2024: 2024-05-19
        response = self.client.get("/liturgical-day?date=2024-05-19&lang=en")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["date"], "2024-05-19")
        self.assertEqual(data["main_day"]["name"], "Pentecost Sunday")
        self.assertEqual(data["main_day"]["color"], "RED")

    def test_liturgical_day_portuguese(self):
        # Pentecost 2024: 2024-05-19 in Portuguese
        response = self.client.get("/liturgical-day?date=2024-05-19&lang=pt")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["main_day"]["name"], "Domingo de Pentecostes")

    def test_invalid_date_format(self):
        response = self.client.get("/liturgical-day?date=invalid-date")
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("detail", data)

if __name__ == "__main__":
    unittest.main()
