from rest_framework import serializers

from assets.models import Cabinet, DataCenter, Room, SecurityZone


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
