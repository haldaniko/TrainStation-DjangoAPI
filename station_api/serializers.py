from rest_framework import serializers
from .models import (
    Crew,
    Station,
    Route,
    Train,
    TrainType,
    Order,
    Ticket,
    Journey
)


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ('id', 'first_name', 'last_name')


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ('id', 'name', 'latitude', 'longitude')


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ('id', 'source', 'destination', 'distance')


class RouteListSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="name"
    )
    destination = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="name"
    )

    class Meta:
        model = Route
        fields = ('id', 'source', 'destination', 'distance')


class RouteDetailSerializer(serializers.ModelSerializer):
    source = StationSerializer(many=False, read_only=True)
    destination = StationSerializer(many=False, read_only=True)

    class Meta:
        model = Route
        fields = ('id', 'source', 'destination', 'distance')


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ('id', 'name')


class TrainSerializer(serializers.ModelSerializer):
    train_type = TrainTypeSerializer()

    class Meta:
        model = Train
        fields = ('id', 'name', 'cargo_num', 'places_in_cargo', 'train_type')


class JourneySerializer(serializers.ModelSerializer):
    route = RouteSerializer()
    train = TrainSerializer()

    class Meta:
        model = Journey
        fields = ('id', 'route', 'train', 'departure_time', 'arrival_time')


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Or use a nested serializer if needed

    class Meta:
        model = Order
        fields = ('id', 'created_at', 'user')


class TicketSerializer(serializers.ModelSerializer):
    journey = JourneySerializer()
    order = OrderSerializer()

    class Meta:
        model = Ticket
        fields = ('id', 'cargo', 'seat', 'journey', 'order')
