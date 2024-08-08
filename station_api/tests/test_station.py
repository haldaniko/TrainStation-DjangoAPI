from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from station_api.models import Station
from django.contrib.auth import get_user_model


class StationTests(APITestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            "admin@myproject.com", "password"
        )
        self.client.force_authenticate(self.admin_user)
        self.station = Station.objects.create(
            name="Central Station", latitude=40.7128, longitude=-74.0060
        )
        self.url = reverse("station:station-list")

    def test_create_station(self):
        """Test creating a station"""
        payload = {"name": "East Station", "latitude": 34.0522, "longitude": -118.2437}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], payload["name"])

    def test_list_stations(self):
        """Test listing stations"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Central Station")

    def test_retrieve_station(self):
        """Test retrieving a station"""
        url = reverse("station:station-detail", kwargs={"pk": self.station.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.station.name)

    def test_update_station(self):
        """Test updating a station"""
        url = reverse("station:station-detail", kwargs={"pk": self.station.id})
        payload = {"name": "North Station", "latitude": 37.7749, "longitude": -122.4194}
        response = self.client.patch(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], payload["name"])

    def test_delete_station(self):
        """Test deleting a station"""
        url = reverse("station:station-detail", kwargs={"pk": self.station.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
