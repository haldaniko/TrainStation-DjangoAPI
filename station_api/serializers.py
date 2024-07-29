from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from user.serializers import UserSerializer
from .models import Crew, Station, Route, Train, TrainType, Order, Ticket, Journey


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longitude")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination")


class RouteListSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(many=False, read_only=True, slug_field="name")
    destination = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="name"
    )

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteDetailSerializer(serializers.ModelSerializer):
    source = StationSerializer(many=False, read_only=True)
    destination = StationSerializer(many=False, read_only=True)

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ("id", "name")


class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = ("id", "name", "cargo_num", "places_in_cargo", "train_type", "image")


class TrainListSerializer(serializers.ModelSerializer):
    train_type = serializers.StringRelatedField()

    class Meta:
        model = Train
        fields = ("id", "name", "cargo_num", "places_in_cargo", "train_type")


class TrainDetailSerializer(serializers.ModelSerializer):
    train_type = TrainTypeSerializer()

    class Meta:
        model = Train
        fields = ("id", "name", "cargo_num", "places_in_cargo", "train_type", "image")


class JourneySerializer(serializers.ModelSerializer):
    departure_time = serializers.DateTimeField()
    arrival_time = serializers.DateTimeField()

    class Meta:
        model = Journey
        fields = ["id", "route", "train", "departure_time", "arrival_time"]


class JourneyListSerializer(serializers.ModelSerializer):
    route = serializers.StringRelatedField()
    train = serializers.StringRelatedField()

    class Meta:
        model = Journey
        fields = ("id", "route", "train", "departure_time", "arrival_time")


class JourneyDetailSerializer(serializers.ModelSerializer):
    route = RouteSerializer()
    train = TrainSerializer()

    class Meta:
        model = Journey
        fields = ("id", "route", "train", "departure_time", "arrival_time")


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("id", "created_at", "user")


class OrderListSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Order
        fields = ("id", "created_at", "user")


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(attrs["seat"], attrs["journey"], ValidationError)
        return data

    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "journey", "order")


class TicketListSerializer(serializers.ModelSerializer):
    journey = serializers.StringRelatedField()
    order = serializers.StringRelatedField()

    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "journey", "order")


class TicketDetailSerializer(serializers.ModelSerializer):
    journey = JourneySerializer()
    order = OrderSerializer()

    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "journey", "order")


class OrderDetailSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=True, source="ticket_set")
    user = UserSerializer()

    class Meta:
        model = Order
        fields = ("id", "created_at", "user", "tickets")
