from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import BaseParser


class ParserFactory:
    """解析器工厂 - 根据厂商和设备类型分发到对应解析器"""

    _registry: dict[tuple[str, str], type[BaseParser]] = {}

    _vendor_aliases: dict[str, str] = {
        "H3C": "H3C", "华三": "H3C", "新华三": "H3C", "h3c": "H3C",
        "华为": "Huawei", "Huawei": "Huawei", "huawei": "Huawei",
        "迈普": "Maipu", "Maipu": "Maipu",
        "锐捷": "Ruijie", "Ruijie": "Ruijie",
        "思科": "Cisco", "Cisco": "Cisco",
        "山石": "Hillstone", "Hillstone": "Hillstone",
        "A10": "A10", "a10": "A10",
        "F5": "F5", "f5": "F5",
    }

    @classmethod
    def register(cls, vendor: str, device_type: str):
        def decorator(parser_cls: type[BaseParser]) -> type[BaseParser]:
            cls._registry[(vendor, device_type)] = parser_cls
            return parser_cls
        return decorator

    @classmethod
    def _normalize_vendor(cls, vendor_name: str) -> str:
        if not vendor_name:
            return ""
        if vendor_name in cls._vendor_aliases:
            return cls._vendor_aliases[vendor_name]
        lower = vendor_name.lower()
        for alias, canonical in cls._vendor_aliases.items():
            if alias.lower() == lower:
                return canonical
        return vendor_name

    @classmethod
    def get_parser(cls, device) -> BaseParser:
        vendor = device.device_model.vendor.name
        device_type = device.device_type
        normalized = cls._normalize_vendor(vendor)
        parser_cls = cls._registry.get((normalized, device_type))
        if not parser_cls:
            raise ValueError(f"未注册的解析器: vendor={vendor!r}, type={device_type!r}")
        return parser_cls()

    @classmethod
    def get_parser_by_keys(cls, vendor: str, device_type: str) -> BaseParser:
        normalized = cls._normalize_vendor(vendor)
        parser_cls = cls._registry.get((normalized, device_type))
        if not parser_cls:
            raise ValueError(f"未注册的解析器: vendor={vendor!r}, type={device_type!r}")
        return parser_cls()

    @classmethod
    def available_parsers(cls) -> list[tuple[str, str]]:
        return list(cls._registry.keys())
