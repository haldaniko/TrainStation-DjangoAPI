from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from station_api.models import Crew


class CrewTests(APITestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            'admin@myproject.com', 'password')
        self.client.force_authenticate(self.admin_user)
        self.crew = Crew.objects.create(first_name='John', last_name='Doe')
        self.url = reverse('station:crew-list')

    def test_create_crew(self):
        """Test creating a crew member"""
        payload = {'first_name': 'Jane', 'last_name': 'Doe'}
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['first_name'], payload['first_name'])
        self.assertEqual(response.data['last_name'], payload['last_name'])

    def test_list_crew(self):
        """Test listing crew members"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        crew_data = response.data[0]
        self.assertEqual(crew_data['first_name'], self.crew.first_name)
        self.assertEqual(crew_data['last_name'], self.crew.last_name)

    def test_retrieve_crew(self):
        """Test retrieving a crew member"""
        url = reverse('station:crew-detail', kwargs={'pk': self.crew.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], self.crew.first_name)
        self.assertEqual(response.data['last_name'], self.crew.last_name)

    def test_update_crew(self):
        """Test updating a crew member"""
        url = reverse('station:crew-detail', kwargs={'pk': self.crew.id})
        payload = {'first_name': 'Jack', 'last_name': 'Smith'}
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], payload['first_name'])
        self.assertEqual(response.data['last_name'], payload['last_name'])

    def test_delete_crew(self):
        """Test deleting a crew member"""
        url = reverse('station:crew-detail', kwargs={'pk': self.crew.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
