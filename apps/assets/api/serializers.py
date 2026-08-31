from rest_framework import serializers

from assets.models import (
    Cabinet,
    DataCenter,
    Device,
    DeviceAccount,
    DeviceConfig,
    DeviceConnection,
    DeviceModel,
    Interface,
    NtpConfig,
    Room,
    SecurityZone,
    SnmpConfig,
    SyslogConfig,
    Vendor,
    Vlan,
    Vrf,
)


class SecurityZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityZone
        fields = ("id", "name", "color", "description", "created_at")
        read_only_fields = ("id", "created_at")


class DataCenterSerializer(serializers.ModelSerializer):
    room_count = serializers.IntegerField(source="rooms.count", read_only=True)
    cabinet_count = serializers.SerializerMethodField()

    class Meta:
        model = DataCenter
        fields = ("id", "name", "address", "contact", "phone", "remark",
                  "room_count", "cabinet_count", "created_at")
        read_only_fields = ("id", "created_at")

    def get_cabinet_count(self, obj) -> int:
        return Cabinet.objects.filter(room__datacenter=obj).count()


class RoomSerializer(serializers.ModelSerializer):
    datacenter_name = serializers.CharField(source="datacenter.name", read_only=True)
    cabinet_count = serializers.IntegerField(source="cabinets.count", read_only=True)

    class Meta:
        model = Room
        fields = ("id", "name", "datacenter", "datacenter_name", "contact",
                  "remark", "cabinet_count", "created_at")
        read_only_fields = ("id", "created_at")


class CabinetSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source="room.name", read_only=True)
    datacenter_name = serializers.CharField(source="room.datacenter.name", read_only=True)

    class Meta:
        model = Cabinet
        fields = ("id", "name", "row", "room", "room_name", "datacenter_name",
                  "total_u", "power_capacity", "status", "remark", "created_at")
        read_only_fields = ("id", "created_at")


class VendorSerializer(serializers.ModelSerializer):
    model_count = serializers.IntegerField(source="device_models.count", read_only=True)

    class Meta:
        model = Vendor
        fields = ("id", "name", "name_en", "abbr", "model_count")
        read_only_fields = ("id",)


class DeviceModelSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source="vendor.name", read_only=True)

    class Meta:
        model = DeviceModel
        fields = ("id", "name", "vendor", "vendor_name")
        read_only_fields = ("id",)


class DeviceSerializer(serializers.ModelSerializer):
    idc_name = serializers.CharField(source="idc.name", read_only=True, default="")
    cabinet_name = serializers.CharField(source="cabinet.name", read_only=True, default="")
    room_name = serializers.CharField(source="cabinet.room.name", read_only=True, default="")
    security_zone_name = serializers.CharField(source="security_zone.name", read_only=True, default="")
    device_model_name = serializers.CharField(source="device_model.name", read_only=True, default="")
    device_type_display = serializers.SerializerMethodField()

    def get_device_type_display(self, obj):
        return obj.get_device_type_display() or ""

    class Meta:
        model = Device
        fields = ("id", "hostname", "device_type", "device_type_display", "device_model",
                  "device_model_name", "idc", "idc_name", "cabinet", "cabinet_name",
                  "room_name", "security_zone", "security_zone_name", "u_position",
                  "height", "ip_address", "remark", "created_at")
        read_only_fields = ("id", "created_at")


class DeviceConfigSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source="device.hostname", read_only=True)

    class Meta:
        model = DeviceConfig
        fields = ("id", "device", "device_name", "git_commit_hash", "config_json",
                  "parse_duration", "collected_at")
        read_only_fields = ("id", "collected_at")


class DeviceConnectionSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source="device.hostname", read_only=True, default="")

    class Meta:
        model = DeviceConnection
        fields = ("id", "device", "device_name", "address", "connection_type",
                  "driver", "port", "account_type", "username", "enabled", "created_at")
        read_only_fields = ("id", "created_at")
        extra_kwargs = {"password": {"write_only": True}}


class VlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vlan
        fields = ("id", "vid", "name", "description")
        read_only_fields = ("id",)


class VrfSerializer(serializers.ModelSerializer):
    device_hostname = serializers.CharField(source="device.hostname", read_only=True, default="")

    class Meta:
        model = Vrf
        fields = ("id", "device", "device_hostname", "name", "rd", "description", "is_active", "created_at")
        read_only_fields = ("id", "created_at")


class InterfaceSerializer(serializers.ModelSerializer):
    device_hostname = serializers.CharField(source="device.hostname", read_only=True, default="")
    vrf_name = serializers.CharField(source="vrf.name", read_only=True, default="")

    class Meta:
        model = Interface
        fields = ("id", "device", "device_hostname", "interface", "description", "enabled",
                  "mode", "vlans", "vrf", "vrf_name", "type", "combo_type",
                  "ip_address", "subnet_mask", "is_active", "created_at")
        read_only_fields = ("id", "created_at")


class DeviceAccountSerializer(serializers.ModelSerializer):
    device_hostname = serializers.CharField(source="device.hostname", read_only=True, default="")

    class Meta:
        model = DeviceAccount
        fields = ("id", "device", "device_hostname", "username", "auth_type",
                  "privilege", "enabled", "description", "is_active", "created_at")
        read_only_fields = ("id", "created_at")


class SnmpConfigSerializer(serializers.ModelSerializer):
    device_hostname = serializers.CharField(source="device.hostname", read_only=True, default="")

    class Meta:
        model = SnmpConfig
        fields = ("id", "device", "device_hostname", "version", "community_read",
                  "community_write", "port", "trap_enabled", "trap_server", "trap_port",
                  "enabled", "created_at")
        read_only_fields = ("id", "created_at")


class NtpConfigSerializer(serializers.ModelSerializer):
    device_hostname = serializers.CharField(source="device.hostname", read_only=True, default="")

    class Meta:
        model = NtpConfig
        fields = ("id", "device", "device_hostname", "server1", "server2", "server3",
                  "timezone", "sync_interval", "enabled", "created_at")
        read_only_fields = ("id", "created_at")


class SyslogConfigSerializer(serializers.ModelSerializer):
    device_hostname = serializers.CharField(source="device.hostname", read_only=True, default="")

    class Meta:
        model = SyslogConfig
        fields = ("id", "device", "device_hostname", "server1", "server2", "port",
                  "facility", "level", "enabled", "created_at")
        read_only_fields = ("id", "created_at")
