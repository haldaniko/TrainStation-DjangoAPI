from django.contrib.auth import get_user_model
from django.urls import reverse
from geopy.distance import geodesic
from rest_framework import status
from rest_framework.test import APITestCase
from station_api.models import Route, Station


class RouteTests(APITestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            'admin@myproject.com', 'password')
        self.client.force_authenticate(self.admin_user)

        self.station_a = Station.objects.create(name='Station A', latitude=40.7128, longitude=-74.0060)
        self.station_b = Station.objects.create(name='Station B', latitude=34.0522, longitude=-118.2437)

        self.route = Route.objects.create(source=self.station_a, destination=self.station_b)
        self.url = reverse('station:route-list')

    def test_create_route(self):
        payload = {'source': self.station_a.id, 'destination': self.station_b.id}
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['source'], payload['source'])
        self.assertEqual(response.data['destination'], payload['destination'])

    def test_list_route(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        route_data = response.data[0]
        self.assertEqual(route_data['source'], self.station_a.name)
        self.assertEqual(route_data['destination'], self.station_b.name)

    def test_retrieve_route(self):
        url = reverse('station:route-detail', kwargs={'pk': self.route.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['source']["id"], self.station_a.id)
        self.assertEqual(response.data['destination']["id"], self.station_b.id)

    def test_update_route(self):
        url = reverse('station:route-detail', kwargs={'pk': self.route.id})
        new_station = Station.objects.create(name='Station C', latitude=51.5074, longitude=-0.1278)
        payload = {'source': self.station_a.id, 'destination': new_station.id}
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['source'], payload['source'])
        self.assertEqual(response.data['destination'], payload['destination'])

    def test_delete_route(self):
        url = reverse('station:route-detail', kwargs={'pk': self.route.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_route_distance(self):
        url = reverse('station:route-detail', kwargs={'pk': self.route.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('distance', response.data)
        self.assertAlmostEqual(
            response.data['distance'],
            geodesic((40.7128, 74.0060),
                     (34.0522, 118.2437)).kilometers,
            places=1)
