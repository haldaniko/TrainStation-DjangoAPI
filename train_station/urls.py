from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/user/", include("user.urls", namespace="user")),
    path("api/station/", include("station_api.urls", namespace="station")),
]
