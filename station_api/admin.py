from django.contrib import admin

from .models import (
    Crew,
    Station,
    Route,
    Train,
    TrainType,
    Order,
    Ticket,
    Journey)

admin.site.register(Crew)
admin.site.register(Station)
admin.site.register(Route)
admin.site.register(Train)
admin.site.register(TrainType)
admin.site.register(Order)
admin.site.register(Ticket)
admin.site.register(Journey)
