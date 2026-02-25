from django.test import TestCase
from rest_framework.test import APIClient
from unittest.mock import patch

class SearchTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    @patch("search.views.requests.get")
    def test_search_returns_results(self, mock_get):
        mock_get.return_value.json.return_value = [
            {
                "title": "Apartment",
                "location": {"city": "Novi Sad"},
                "price_per_night": 50,
                "guests": 3,
                "amenities": ["wifi"]
            }
        ]

        response = self.client.get("/api/search/?city=Novi Sad")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    @patch("search.views.requests.get")
    def test_invalid_date(self, mock_get):
        mock_get.return_value.json.return_value = []

        response = self.client.get(
            "/api/search/?start_date=2025-10-10&end_date=2025-10-01"
        )

        self.assertEqual(response.status_code, 400)
