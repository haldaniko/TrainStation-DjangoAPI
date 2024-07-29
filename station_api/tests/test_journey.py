from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from station_api.models import Journey, Route, Train, Station, TrainType
from datetime import datetime, timedelta


class JourneyTests(APITestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            'admin@myproject.com', 'password')
        self.client.force_authenticate(self.admin_user)

        self.station_a = Station.objects.create(name='Station A', latitude=40.7128, longitude=-74.0060)
        self.station_b = Station.objects.create(name='Station B', latitude=34.0522, longitude=-118.2437)

        self.route = Route.objects.create(source=self.station_a, destination=self.station_b)
        self.train_type = TrainType.objects.create(name='Express')
        self.train = Train.objects.create(
            name='Train 101',
            cargo_num=10,
            places_in_cargo=100,
            train_type=self.train_type
        )

        departure_datetime_str = "2024-07-27 08:00:00"
        arrival_datetime_str = "2024-07-27 13:00:00"

        self.departure_time = timezone.make_aware(datetime.strptime(departure_datetime_str, "%Y-%m-%d %H:%M:%S"))
        self.arrival_time = timezone.make_aware(datetime.strptime(arrival_datetime_str, "%Y-%m-%d %H:%M:%S"))

        self.journey = Journey.objects.create(
            route=self.route,
            train=self.train,
            departure_time=self.departure_time,
            arrival_time=self.arrival_time
        )
        self.url = reverse('station:journey-list')

    def test_create_journey(self):
        payload = {
            'route': self.route.id,
            'train': self.train.id,
            'departure_time': self.departure_time.isoformat(),  # ISO формат времени
            'arrival_time': self.arrival_time.isoformat()       # ISO формат времени
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['route'], payload['route'])
        self.assertEqual(response.data['train'], payload['train'])
        # Приведение к формату с учетом часового пояса
        self.assertEqual(response.data['departure_time'].replace('Z', '+00:00'), payload['departure_time'])
        self.assertEqual(response.data['arrival_time'].replace('Z', '+00:00'), payload['arrival_time'])

    def test_list_journey(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        journey_data = response.data[0]
        self.assertEqual(journey_data['route'], str(self.route))
        self.assertEqual(journey_data['train'], self.train.name)
        self.assertEqual(journey_data['departure_time'].replace('Z', '+00:00'), self.departure_time.isoformat())
        self.assertEqual(journey_data['arrival_time'].replace('Z', '+00:00'), self.arrival_time.isoformat())

    def test_retrieve_journey(self):
        url = reverse('station:journey-detail', kwargs={'pk': self.journey.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['route']["id"], self.route.id)
        self.assertEqual(response.data['train']["id"], self.train.id)
        self.assertEqual(response.data['departure_time'].replace('Z', '+00:00'), self.departure_time.isoformat())
        self.assertEqual(response.data['arrival_time'].replace('Z', '+00:00'), self.arrival_time.isoformat())

    def test_update_journey(self):
        url = reverse('station:journey-detail', kwargs={'pk': self.journey.id})
        new_arrival_time = self.departure_time + timedelta(hours=6)
        payload = {
            'route': self.route.id,
            'train': self.train.id,
            'departure_time': self.departure_time.isoformat(),
            'arrival_time': new_arrival_time.isoformat()
        }
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['route'], payload['route'])
        self.assertEqual(response.data['train'], payload['train'])
        self.assertEqual(response.data['departure_time'].replace('Z', '+00:00'), payload['departure_time'])
        self.assertEqual(response.data['arrival_time'].replace('Z', '+00:00'), payload['arrival_time'])

    def test_delete_journey(self):
        url = reverse('station:journey-detail', kwargs={'pk': self.journey.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
