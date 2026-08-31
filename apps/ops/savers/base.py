"""Saver 基类 - 自动注册"""
from abc import ABC, abstractmethod
from logging import getLogger
from typing import Any

logger = getLogger(__name__)


class BaseSaver(ABC):
    """基类，子类定义 device_types 和 keys 类属性即自动注册"""

    device_types: list[str] = []
    keys: list[str] = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.device_types and cls.keys:
            from .registry import _registry
            for dt in cls.device_types:
                for key in cls.keys:
                    _registry[(dt, key)] = cls

    @abstractmethod
    def save(self, device, parsed_data: dict) -> tuple[int, int]:
        """保存数据，返回 (created_count, updated_count)"""

    def _safe_int(self, value: Any) -> int | None:
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
