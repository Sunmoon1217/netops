from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from assets.models import Cabinet, DataCenter, Room, SecurityZone

from .serializers import CabinetSerializer, DataCenterSerializer, RoomSerializer, SecurityZoneSerializer


def overview(request):
    """DCIM 概览统计"""
    return JsonResponse(
        {
            "total_datacenters": DataCenter.objects.count(),
            "total_rooms": Room.objects.count(),
            "total_cabinets": Cabinet.objects.count(),
            "active_cabinets": Cabinet.objects.filter(status="active").count(),
        }
    )


class SecurityZoneViewSet(viewsets.ModelViewSet):
    queryset = SecurityZone.objects.all()
    serializer_class = SecurityZoneSerializer
    permission_classes = (AllowAny,)
    search_fields = ("name",)
    ordering_fields = ("name", "created_at")


class DataCenterViewSet(viewsets.ModelViewSet):
    queryset = DataCenter.objects.all()
    serializer_class = DataCenterSerializer
    permission_classes = (AllowAny,)
    search_fields = ("name", "address")
    ordering_fields = ("name", "created_at")


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.select_related("datacenter").all()
    serializer_class = RoomSerializer
    permission_classes = (AllowAny,)
    search_fields = ("name", "datacenter__name")
    ordering_fields = ("name", "created_at")

    def get_queryset(self):
        qs = super().get_queryset()
        datacenter = self.request.query_params.get("datacenter")
        if datacenter:
            qs = qs.filter(datacenter_id=datacenter)
        return qs


class CabinetViewSet(viewsets.ModelViewSet):
    queryset = Cabinet.objects.select_related("room", "room__datacenter").all()
    serializer_class = CabinetSerializer
    permission_classes = (AllowAny,)
    search_fields = ("name", "room__name", "room__datacenter__name")
    ordering_fields = ("name", "status", "created_at")

    def get_queryset(self):
        qs = super().get_queryset()
        room = self.request.query_params.get("room")
        if room:
            qs = qs.filter(room_id=room)
        datacenter = self.request.query_params.get("datacenter")
        if datacenter:
            qs = qs.filter(room__datacenter_id=datacenter)
        status = self.request.query_params.get("status")
        if status:
            qs = qs.filter(status=status)
        return qs


class DeviceViewSet(viewsets.ModelViewSet):
    from assets.models import Device

    from .serializers import DeviceSerializer

    queryset = Device.objects.select_related("idc").all()
    serializer_class = DeviceSerializer
    permission_classes = (AllowAny,)
    search_fields = ("hostname", "ip_address")
    ordering_fields = ("hostname", "created_at")

    def get_queryset(self):
        qs = super().get_queryset()
        device_type = self.request.query_params.get("device_type")
        if device_type:
            qs = qs.filter(device_type=device_type)
        idc = self.request.query_params.get("idc")
        if idc:
            qs = qs.filter(idc_id=idc)
        return qs


class DeviceConfigViewSet(viewsets.ModelViewSet):
    from assets.models import DeviceConfig

    from .serializers import DeviceConfigSerializer

    queryset = DeviceConfig.objects.select_related("device").all()
    serializer_class = DeviceConfigSerializer
    permission_classes = (AllowAny,)
    ordering_fields = ("collected_at",)

    def get_queryset(self):
        qs = super().get_queryset()
        device_id = self.request.query_params.get("device")
        if device_id:
            qs = qs.filter(device_id=device_id)
        return qs


@api_view(["POST"])
@permission_classes([AllowAny])
def import_devices(request):
    """导入设备 Excel"""
    from openpyxl import load_workbook

    excel_file = request.FILES.get("file")
    if not excel_file:
        return Response({"error": "请上传 Excel 文件"}, status=400)

    try:
        wb = load_workbook(excel_file, read_only=True, data_only=True)
    except Exception as e:
        return Response({"error": f"文件格式错误: {e}"}, status=400)

    from assets.models import DataCenter, Device

    results = {"created": 0, "updated": 0, "errors": []}

    for sheet_name in wb.sheetnames:
        if "设备" not in sheet_name:
            continue
        ws = wb[sheet_name]
        for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            if not row[0]:
                continue
            hostname = str(row[0]).strip()
            device_type = str(row[1] or "switch").strip()
            ip_address = str(row[2] or "").strip()
            idc_name = str(row[3] or "").strip()
            remark = str(row[4] or "").strip()

            idc = None
            if idc_name:
                idc = DataCenter.objects.filter(name=idc_name).first()

            try:
                _, is_created = Device.objects.update_or_create(
                    hostname=hostname,
                    defaults={
                        "device_type": device_type,
                        "ip_address": ip_address,
                        "idc": idc,
                        "remark": remark,
                    },
                )
                if is_created:
                    results["created"] += 1
                else:
                    results["updated"] += 1
            except Exception as e:
                results["errors"].append(f"行 {row_idx}: {e}")

    wb.close()
    return Response({"success": True, **results})
