from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from station_api.models import TrainType


class TrainTypeTests(APITestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            'admin@myproject.com', 'password')
        self.client.force_authenticate(self.admin_user)
        self.train_type = TrainType.objects.create(name='Express')
        self.url = reverse('station:traintype-list')

    def test_create_traintype(self):
        payload = {'name': 'Freight'}
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], payload['name'])

    def test_list_traintype(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        traindata = response.data[0]
        self.assertEqual(traindata['name'], self.train_type.name)

    def test_retrieve_traintype(self):
        url = reverse('station:traintype-detail', kwargs={'pk': self.train_type.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.train_type.name)

    def test_update_traintype(self):
        url = reverse('station:traintype-detail', kwargs={'pk': self.train_type.id})
        payload = {'name': 'High-Speed'}
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], payload['name'])

    def test_delete_traintype(self):
        url = reverse('station:traintype-detail', kwargs={'pk': self.train_type.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
