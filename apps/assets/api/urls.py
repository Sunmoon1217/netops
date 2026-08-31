from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter(trailing_slash=True)
router.register(r"security-zones", views.SecurityZoneViewSet, basename="security-zone")
router.register(r"datacenters", views.DataCenterViewSet, basename="datacenter")
router.register(r"rooms", views.RoomViewSet, basename="room")
router.register(r"cabinets", views.CabinetViewSet, basename="cabinet")
router.register(r"vendors", views.VendorViewSet, basename="vendor")
router.register(r"device-models", views.DeviceModelViewSet, basename="device-model")
router.register(r"devices", views.DeviceViewSet, basename="device")
router.register(r"device-configs", views.DeviceConfigViewSet, basename="device-config")
router.register(r"device-connections", views.DeviceConnectionViewSet, basename="device-connection")
router.register(r"vlans", views.VlanViewSet, basename="vlan")
router.register(r"vrfs", views.VrfViewSet, basename="vrf")
router.register(r"interfaces", views.InterfaceViewSet, basename="interface")
router.register(r"device-accounts", views.DeviceAccountViewSet, basename="device-account")
router.register(r"snmp-configs", views.SnmpConfigViewSet, basename="snmp-config")
router.register(r"ntp-configs", views.NtpConfigViewSet, basename="ntp-config")
router.register(r"syslog-configs", views.SyslogConfigViewSet, basename="syslog-config")

urlpatterns = [
    path("assets/", include(router.urls)),
    path("assets/overview/", views.overview, name="dcim-overview"),
    path("assets/import-devices/", views.import_excel, name="import-devices"),
]
