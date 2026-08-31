"""路由数据保存器"""
from logging import getLogger

from assets.models import Vrf

from .base import BaseSaver

logger = getLogger(__name__)


class VrfSaver(BaseSaver):
    device_types = ["switch", "router"]
    keys = ["vrfs", "vpn_instances"]

    def save(self, device, parsed_data: dict) -> tuple[int, int]:
        vrfs = parsed_data.get("vrfs", parsed_data.get("vpn_instances", []))
        if not vrfs:
            return (0, 0)

        created, updated = 0, 0
        for vrf in vrfs:
            vrf_name = vrf.get("vrf", vrf.get("name"))
            if not vrf_name:
                continue
            _, is_created = Vrf.objects.update_or_create(
                device=device, name=vrf_name,
                defaults={
                    "rd": vrf.get("rd", ""),
                    "description": vrf.get("description", ""),
                },
            )
            created += 1 if is_created else 0
            updated += 0 if is_created else 1
        return (created, updated)
