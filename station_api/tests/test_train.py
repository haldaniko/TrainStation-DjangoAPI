from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from PIL import Image
import tempfile
import os

from station_api.models import Train, TrainType, Crew, Station
from rest_framework.authtoken.models import Token


class TrainTests(APITestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            'admin@myproject.com', 'password')
        self.client.force_authenticate(self.admin_user)
        self.train_type = TrainType.objects.create(name='Express')
        self.train = Train.objects.create(
            name='Train 101',
            cargo_num=10,
            places_in_cargo=100,
            train_type=self.train_type
        )
        self.url = reverse('station:train-list')

    def test_upload_image_to_train(self):
        """Test uploading an image to a train"""
        url = reverse('station:train-detail', kwargs={'pk': self.train.id})
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            response = self.client.patch(url, {"image": ntf}, format="multipart")
        self.train.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("image", response.data)
        self.assertTrue(os.path.exists(self.train.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = reverse('station:train-detail', kwargs={'pk': self.train.id})
        response = self.client.patch(url, {"image": "not an image"}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_train_list(self):
        """Test posting an image when creating a train"""
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            response = self.client.post(
                self.url,
                {
                    "name": "New Train",
                    "cargo_num": 456,
                    "places_in_cargo": 150,
                    "train_type": self.train_type.id,
                    "image": ntf,
                },
                format="multipart",
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        train = Train.objects.get(name="New Train")
        self.assertTrue(train.image)

    def test_create_train(self):
        payload = {
            'name': 'Train 102',
            'cargo_num': 20,
            'places_in_cargo': 200,
            'train_type': self.train_type.id
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], payload['name'])
        self.assertEqual(response.data['cargo_num'], payload['cargo_num'])
        self.assertEqual(response.data['places_in_cargo'], payload['places_in_cargo'])
        self.assertEqual(response.data['train_type'], payload['train_type'])

    def test_list_train(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        train_data = response.data[0]
        self.assertEqual(train_data['name'], self.train.name)
        self.assertEqual(train_data['cargo_num'], self.train.cargo_num)
        self.assertEqual(train_data['places_in_cargo'], self.train.places_in_cargo)
        self.assertEqual(train_data['train_type'], self.train.train_type.name)

    def test_retrieve_train(self):
        url = reverse('station:train-detail', kwargs={'pk': self.train.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.train.name)
        self.assertEqual(response.data['cargo_num'], self.train.cargo_num)
        self.assertEqual(response.data['places_in_cargo'], self.train.places_in_cargo)
        self.assertEqual(response.data['train_type']["id"], self.train.train_type.id)

    def test_update_train(self):
        url = reverse('station:train-detail', kwargs={'pk': self.train.id})
        payload = {
            'name': 'Train 103',
            'cargo_num': 30,
            'places_in_cargo': 300,
            'train_type': self.train_type.id
        }
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], payload['name'])
        self.assertEqual(response.data['cargo_num'], payload['cargo_num'])
        self.assertEqual(response.data['places_in_cargo'], payload['places_in_cargo'])
        self.assertEqual(response.data['train_type'], payload['train_type'])

    def test_delete_train(self):
        url = reverse('station:train-detail', kwargs={'pk': self.train.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
