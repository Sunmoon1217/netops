"""防火墙数据保存器"""
from logging import getLogger

from .base import BaseSaver

logger = getLogger(__name__)


class AddressBookSaver(BaseSaver):
    device_types = ["firewall"]
    keys = ["address_books", "addresses"]

    def save(self, device, parsed_data: dict) -> tuple[int, int]:
        from assets.models import AddressBook

        address_books = parsed_data.get("address_books", parsed_data.get("addresses", []))
        if not address_books:
            return (0, 0)

        created, updated = 0, 0
        for ab in address_books:
            name = ab.get("name")
            if not name:
                continue
            addresses = ab.get("addresses", [])
            targets = addresses if addresses else [ab]
            for addr in targets:
                _, is_created = AddressBook.objects.update_or_create(
                    device=device, name=name,
                    defaults={
                        "address_type": addr.get("type", "host"),
                        "ip_address": addr.get("ip_address") or addr.get("address"),
                        "ip_netmask": self._safe_int(addr.get("netmask")),
                        "ip_start": addr.get("start"),
                        "ip_end": addr.get("end"),
                        "description": addr.get("description", ""),
                    },
                )
                created += 1 if is_created else 0
                updated += 0 if is_created else 1
        return (created, updated)


class ServiceSaver(BaseSaver):
    device_types = ["firewall"]
    keys = ["services"]

    def save(self, device, parsed_data: dict) -> tuple[int, int]:
        from assets.models import Service

        services = parsed_data.get("services", [])
        if not services:
            return (0, 0)

        created, updated = 0, 0
        for svc in services:
            name = svc.get("name")
            if not name:
                continue
            _, is_created = Service.objects.update_or_create(
                device=device, name=name,
                defaults={
                    "protocol": svc.get("protocol", "tcp"),
                    "port": str(svc.get("port", "")),
                    "port2": str(svc.get("port2", "")),
                    "description": svc.get("description", ""),
                },
            )
            created += 1 if is_created else 0
            updated += 0 if is_created else 1
        return (created, updated)


class PolicySaver(BaseSaver):
    device_types = ["firewall"]
    keys = ["policies", "acl"]

    def save(self, device, parsed_data: dict) -> tuple[int, int]:
        from assets.models import Policy

        policies = parsed_data.get("policies", parsed_data.get("acl", []))
        if not policies:
            return (0, 0)

        created, updated = 0, 0
        for p in policies:
            policy_id = p.get("policy_id", p.get("name", ""))
            if not policy_id:
                continue
            _, is_created = Policy.objects.update_or_create(
                device=device, policy_id=policy_id,
                defaults={
                    "order": p.get("order", 0),
                    "name": p.get("name", policy_id),
                    "action": p.get("action", "allow"),
                    "enabled": p.get("enabled", True),
                    "log": p.get("log", False),
                    "description": p.get("description", ""),
                },
            )
            created += 1 if is_created else 0
            updated += 0 if is_created else 1
        return (created, updated)
