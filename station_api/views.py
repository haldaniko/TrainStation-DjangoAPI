from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets
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
from .serializers import (
    CrewSerializer,
    StationSerializer,
    TrainSerializer,
    TrainTypeSerializer,
    OrderSerializer,
    TicketSerializer,
    JourneySerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    TrainListSerializer,
    TrainDetailSerializer,
    JourneyListSerializer,
    JourneyDetailSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
    TicketListSerializer,
    TicketDetailSerializer,
)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer

    def get_queryset(self):
        """Retrieve the crew with filters"""
        first_name = self.request.query_params.get("first_name")
        last_name = self.request.query_params.get("last_name")

        queryset = self.queryset

        if first_name:
            queryset = queryset.filter(first_name__icontains=first_name)

        if last_name:
            queryset = queryset.filter(last_name__icontains=last_name)
        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "first_name",
                type=str,
                description="Filter by First Name",
                required=False,
            ),
            OpenApiParameter(
                "last_name",
                type=str,
                description="Filter by Last Name",
                required=False,
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all().select_related('source', 'destination')

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer

        if self.action == "retrieve":
            return RouteDetailSerializer

        return RouteSerializer


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all().select_related('train_type')

    def get_serializer_class(self):
        if self.action == "list":
            return TrainListSerializer

        if self.action == "retrieve":
            return TrainDetailSerializer

        return TrainSerializer


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.all().select_related('route', 'train')

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer

        if self.action == "retrieve":
            return JourneyDetailSerializer

        return JourneySerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().select_related('user').prefetch_related('ticket_set')

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        if self.action == "retrieve":
            return OrderDetailSerializer

        return OrderSerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all().select_related('journey', 'order')

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer

        if self.action == "retrieve":
            return TicketDetailSerializer

        return TicketSerializer
