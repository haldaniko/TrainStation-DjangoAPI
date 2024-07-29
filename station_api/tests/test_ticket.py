from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from station_api.models import Journey, Order, Ticket, Station, Route, Train, TrainType
from datetime import datetime, timedelta
import pytz


class TicketTests(APITestCase):
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

        self.departure_time = timezone.make_aware(datetime.strptime("2024-07-27 08:00:00", "%Y-%m-%d %H:%M:%S"))
        self.arrival_time = self.departure_time + timedelta(hours=5)

        self.journey = Journey.objects.create(
            route=self.route,
            train=self.train,
            departure_time=self.departure_time,
            arrival_time=self.arrival_time
        )

        self.user = get_user_model().objects.create_user(
            'user@myproject.com', 'password'
        )

        self.order = Order.objects.create(
            created_at=self.departure_time,
            user=self.user
        )

        self.ticket = Ticket.objects.create(
            cargo=1,
            seat=1,
            journey=self.journey,
            order=self.order
        )

    def test_create_ticket(self):
        payload = {
            'cargo': 2,
            'seat': 2,
            'journey': self.journey.id,
            'order': self.order.id
        }
        response = self.client.post(reverse('station:ticket-list'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['seat'], payload['seat'])
        self.assertEqual(response.data['journey'], payload['journey'])
        self.assertEqual(response.data['order'], payload['order'])

    def test_ticket_unique_together(self):
        # Create ticket with a unique seat for the same journey
        ticket_1 = Ticket.objects.create(
            cargo=1,
            seat=3,
            journey=self.journey,
            order=self.order
        )
        self.assertEqual(ticket_1.seat, 3)

        # Attempt to create another ticket with the same seat in the same journey
        with self.assertRaises(ValidationError):
            Ticket.objects.create(
                cargo=2,
                seat=3,
                journey=self.journey,
                order=self.order
            )

    def test_ticket_order_restriction(self):
        # Create a ticket for a different order
        new_user = get_user_model().objects.create_user('newuser@myproject.com', 'password')
        new_order = Order.objects.create(created_at=self.departure_time, user=new_user)

        ticket = Ticket.objects.create(
            cargo=2,
            seat=4,
            journey=self.journey,
            order=new_order
        )
        self.assertEqual(ticket.seat, 4)
        self.assertEqual(ticket.order, new_order)

    def test_list_tickets(self):
        response = self.client.get(reverse('station:ticket-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only one ticket should exist

    def test_retrieve_ticket(self):
        url = reverse('station:ticket-detail', kwargs={'pk': self.ticket.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['seat'], self.ticket.seat)
        self.assertEqual(response.data['journey']["id"], self.ticket.journey.id)
        self.assertEqual(response.data['order']["id"], self.ticket.order.id)

    def test_delete_ticket(self):
        url = reverse('station:ticket-detail', kwargs={'pk': self.ticket.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Verify ticket is deleted
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
