import logging

from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from assets.models import (
    Cabinet,
    DataCenter,
    Device,
    DeviceConfig,
    DeviceConnection,
    DeviceModel,
    Room,
    SecurityZone,
    Vendor,
)

from .serializers import (
    CabinetSerializer,
    DataCenterSerializer,
    DeviceConfigSerializer,
    DeviceSerializer,
    RoomSerializer,
    SecurityZoneSerializer,
)

logger = logging.getLogger(__name__)


def overview(request):
    """DCIM 概览统计"""
    return JsonResponse({
        "total_datacenters": DataCenter.objects.count(),
        "total_rooms": Room.objects.count(),
        "total_cabinets": Cabinet.objects.count(),
        "active_cabinets": Cabinet.objects.filter(status="active").count(),
    })


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
    queryset = Device.objects.select_related("idc", "cabinet", "security_zone", "device_model").all()
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


# ---------------------------------------------------------------------------
# 导入功能
# ---------------------------------------------------------------------------

CONNECTION_CONFIG_MAP = {
    ("H3C", "switch"): {"connection_type": "napalm", "driver": "h3c_comware"},
    ("H3C", "router"): {"connection_type": "napalm", "driver": "h3c_comware"},
    ("锐捷", "switch"): {"connection_type": "netmiko", "driver": "ruijie_os"},
    ("思科", "firewall"): {"connection_type": "napalm", "driver": "asa"},
    ("山石", "firewall"): {"connection_type": "netmiko", "driver": "hillstone_stoneos"},
    ("F5", "loadbalancer"): {"connection_type": "netmiko", "driver": "f5_ltm"},
    ("A10", "loadbalancer"): {"connection_type": "netmiko", "driver": "a10"},
}


def _get_connection_config(vendor_name, device_type):
    return CONNECTION_CONFIG_MAP.get(
        (vendor_name, device_type),
        {"connection_type": "netmiko", "driver": ""},
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def import_excel(request):
    """导入 Excel 文件，支持多个 Sheet"""
    from openpyxl import load_workbook

    excel_file = request.FILES.get("file")
    if not excel_file:
        return Response({"error": "请上传 Excel 文件"}, status=400)

    try:
        wb = load_workbook(excel_file, read_only=True, data_only=True)
    except Exception as e:
        return Response({"error": f"文件格式错误: {e}"}, status=400)

    results = {}
    sheet_importers = {
        "数据中心": _import_datacenters,
        "机房": _import_rooms,
        "机柜": _import_cabinets,
        "安全区": _import_security_zones,
        "设备": _import_devices,
        "配置文件": _import_configs,
    }

    for sheet_name, importer in sheet_importers.items():
        if sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            try:
                results[sheet_name] = importer(ws)
            except Exception as e:
                logger.error(f"导入 {sheet_name} 失败: {e}")
                results[sheet_name] = {"created": 0, "updated": 0, "errors": [str(e)]}
        else:
            results[sheet_name] = {"created": 0, "updated": 0, "errors": [], "skipped": True}

    wb.close()
    return Response({"success": True, "results": results})


def _import_datacenters(ws):
    created, updated, errors = 0, 0, []
    for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        if not row[0]:
            continue
        name = str(row[0]).strip()
        defaults = {
            "address": str(row[1] or "").strip(),
            "contact": str(row[2] or "").strip(),
            "phone": str(row[3] or "").strip(),
            "remark": str(row[4] or "").strip(),
        }
        try:
            _, is_created = DataCenter.objects.update_or_create(name=name, defaults=defaults)
            created += 1 if is_created else 0
            updated += 0 if is_created else 1
        except Exception as e:
            errors.append(f"行 {row_idx}: {e}")
    return {"created": created, "updated": updated, "errors": errors}


def _import_rooms(ws):
    created, updated, errors = 0, 0, []
    for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        if not row[0] or not row[1]:
            continue
        try:
            dc = DataCenter.objects.get(name=str(row[0]).strip())
            _, is_created = Room.objects.update_or_create(
                datacenter=dc, name=str(row[1]).strip(),
                defaults={"contact": str(row[2] or "").strip(), "remark": str(row[3] or "").strip()},
            )
            created += 1 if is_created else 0
            updated += 0 if is_created else 1
        except DataCenter.DoesNotExist:
            errors.append(f"行 {row_idx}: 数据中心 '{row[0]}' 不存在")
        except Exception as e:
            errors.append(f"行 {row_idx}: {e}")
    return {"created": created, "updated": updated, "errors": errors}


def _import_cabinets(ws):
    created, updated, errors = 0, 0, []
    for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        if not row[0] or not row[1] or not row[2]:
            continue
        try:
            dc = DataCenter.objects.get(name=str(row[0]).strip())
            room = Room.objects.get(datacenter=dc, name=str(row[1]).strip())
            _, is_created = Cabinet.objects.update_or_create(
                room=room, name=str(row[2]).strip(),
                defaults={
                    "row": str(row[3] or "").strip(),
                    "total_u": int(row[4] or 42),
                    "power_capacity": float(row[5]) if row[5] else None,
                    "status": str(row[6] or "active").strip(),
                    "remark": str(row[7] or "").strip(),
                },
            )
            created += 1 if is_created else 0
            updated += 0 if is_created else 1
        except DataCenter.DoesNotExist:
            errors.append(f"行 {row_idx}: 数据中心 '{row[0]}' 不存在")
        except Room.DoesNotExist:
            errors.append(f"行 {row_idx}: 机房 '{row[1]}' 不存在")
        except Exception as e:
            errors.append(f"行 {row_idx}: {e}")
    return {"created": created, "updated": updated, "errors": errors}


def _import_security_zones(ws):
    created, updated, errors = 0, 0, []
    for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        if not row[0]:
            continue
        try:
            _, is_created = SecurityZone.objects.update_or_create(
                name=str(row[0]).strip(),
                defaults={"color": str(row[1] or "#3b82f6").strip(), "description": str(row[2] or "").strip()},
            )
            created += 1 if is_created else 0
            updated += 0 if is_created else 1
        except Exception as e:
            errors.append(f"行 {row_idx}: {e}")
    return {"created": created, "updated": updated, "errors": errors}


def _import_devices(ws):
    created, updated, errors = 0, 0, []
    for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        if not row[0]:
            continue
        hostname = str(row[0]).strip()
        device_type = str(row[2] or "switch").strip()
        ip_address = str(row[1] or "").strip()

        # 厂商和型号
        vendor = None
        device_model = None
        vendor_name = str(row[3] or "").strip()
        model_name = str(row[4] or "").strip()
        if vendor_name:
            vendor, _ = Vendor.objects.get_or_create(name=vendor_name)
        if model_name and vendor:
            device_model, _ = DeviceModel.objects.get_or_create(name=model_name, vendor=vendor)

        # 机柜
        dc = None
        cabinet = None
        dc_name = str(row[5] or "").strip()
        room_name = str(row[6] or "").strip()
        cab_name = str(row[7] or "").strip()
        if dc_name and room_name and cab_name:
            try:
                dc = DataCenter.objects.get(name=dc_name)
                room = Room.objects.get(datacenter=dc, name=room_name)
                cabinet = Cabinet.objects.get(room=room, name=cab_name)
            except (DataCenter.DoesNotExist, Room.DoesNotExist, Cabinet.DoesNotExist):
                errors.append(f"行 {row_idx}: 机柜路径 '{dc_name}/{room_name}/{cab_name}' 不存在")

        # 安全区
        security_zone = None
        zone_name = str(row[8] or "").strip()
        if zone_name:
            security_zone = SecurityZone.objects.filter(name=zone_name).first()

        device_defaults = {
            "device_type": device_type,
            "ip_address": ip_address,
            "device_model": device_model,
            "idc": dc,
            "cabinet": cabinet,
            "security_zone": security_zone,
            "u_position": int(row[9]) if row[9] else None,
            "height": int(row[10] or 1),
            "remark": str(row[11] or "").strip(),
        }

        try:
            device, is_created = Device.objects.update_or_create(
                hostname=hostname, defaults=device_defaults
            )
            created += 1 if is_created else 0
            updated += 0 if is_created else 1
        except Exception as e:
            errors.append(f"行 {row_idx}: {e}")
            continue

        # 连接信息（第12-16列）
        account_type = str(row[12] or "").strip()
        username = str(row[13] or "").strip()
        password = str(row[14] or "").strip()
        if username and password:
            conn_config = _get_connection_config(vendor_name, device_type)
            conn_defaults = {
                "connection_type": conn_config["connection_type"],
                "driver": conn_config["driver"],
                "account_type": account_type or "admin",
                "username": username,
                "password": password,
                "enable_password": str(row[15] or "").strip(),
                "port": int(row[16] or 22) if row[16] else 22,
                "timeout": int(row[17] or 30) if row[17] else 30,
            }
            try:
                DeviceConnection.objects.update_or_create(
                    device=device, account_type=account_type or "admin", defaults=conn_defaults
                )
            except Exception as e:
                errors.append(f"行 {row_idx} 连接: {e}")

    return {"created": created, "updated": updated, "errors": errors}


def _import_configs(ws):
    """导入设备配置文件"""
    from pathlib import Path

    from ops.config_repo import CONFIG_REPO_PATH, save_config

    created, skipped, errors = 0, 0, []

    for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        if not row[0]:
            continue

        hostname = str(row[0]).strip()
        filename = row[1] and str(row[1]).strip() or hostname + ".txt"
        config_dir = str(row[2] or "").strip()

        try:
            device = Device.objects.get(hostname=hostname)
        except Device.DoesNotExist:
            errors.append(f"行 {row_idx}: 设备 '{hostname}' 不存在，请先导入设备")
            continue

        if config_dir:
            config_path = Path(config_dir) / filename
        else:
            config_path = CONFIG_REPO_PATH / hostname / filename

        if not config_path.exists():
            errors.append(f"行 {row_idx}: 配置文件不存在: {config_path}")
            continue

        try:
            config_text = config_path.read_text(encoding="utf-8")
        except Exception as e:
            errors.append(f"行 {row_idx}: 读取失败: {e}")
            continue

        if not config_text.strip():
            errors.append(f"行 {row_idx}: 配置文件为空")
            continue

        try:
            commit_hash = save_config(hostname, config_text, message=f"import: {hostname} config")
        except Exception as e:
            errors.append(f"行 {row_idx}: 保存到 Git 失败: {e}")
            continue

        DeviceConfig.objects.update_or_create(
            device=device, git_commit_hash=commit_hash,
            defaults={"config_json": {}},
        )
        created += 1

    return {"created": created, "skipped": skipped, "errors": errors}
