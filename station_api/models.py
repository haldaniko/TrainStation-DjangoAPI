import os
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from geopy.distance import geodesic

from user.models import User


def image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.name)}-{uuid.uuid4()}{extension}"

    return os.path.join(f"uploads/trains/", filename)


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Station(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name="route_source"
    )
    destination = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name="route_destination"
    )

    @property
    def distance(self):
        if self.source and self.destination:
            source_coords = (self.source.latitude, self.source.longitude)
            destination_coords = (self.destination.latitude, self.destination.longitude)
            return geodesic(source_coords, destination_coords).kilometers
        return None

    def __str__(self):
        return f"From {self.source} to {self.destination}"


class TrainType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Train(models.Model):
    name = models.CharField(max_length=255)
    cargo_num = models.IntegerField()
    places_in_cargo = models.IntegerField()
    train_type = models.ForeignKey(TrainType, on_delete=models.CASCADE)
    image = models.ImageField(null=True, upload_to=image_file_path)

    def __str__(self):
        return self.name


class Journey(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def __str__(self):
        return f"{self.route} on {self.train}"


class Order(models.Model):
    created_at = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Order at {self.created_at} by {self.user}"


class Ticket(models.Model):
    cargo = models.IntegerField()
    seat = models.IntegerField()
    journey = models.ForeignKey("Journey", on_delete=models.CASCADE)
    order = models.ForeignKey("Order", on_delete=models.CASCADE)

    @staticmethod
    def validate_ticket(seat, journey, error_to_raise):
        if Ticket.objects.filter(seat=seat, journey=journey).exists():
            raise error_to_raise({"seat": f"The seat is alredy taken"})

    def clean(self):
        Ticket.validate_ticket(
            self.seat,
            self.journey,
            ValidationError,
        )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        return f"Seat {self.seat}, {self.journey}"

    class Meta:
        unique_together = ("journey", "seat")
        ordering = ["seat"]
