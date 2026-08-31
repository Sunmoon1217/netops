from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter(trailing_slash=True)
router.register(r"security-zones", views.SecurityZoneViewSet, basename="security-zone")
router.register(r"datacenters", views.DataCenterViewSet, basename="datacenter")
router.register(r"rooms", views.RoomViewSet, basename="room")
router.register(r"cabinets", views.CabinetViewSet, basename="cabinet")

urlpatterns = [
    path("dcim/", include(router.urls)),
    path("dcim/overview/", views.overview, name="dcim-overview"),
]
