"""H3C Comware 配置解析器 - 纯函数，无 Django 依赖。"""

from typing import Any

from .base import BaseParser
from .factory import ParserFactory


def _extract_ttp_result(result: list) -> dict[str, Any]:
    """从 TTP 原始结果中提取第一个匹配组的字典。"""
    if result and result[0]:
        return result[0][0]
    return {}


@ParserFactory.register("H3C", "switch")
class H3CSwitchParser(BaseParser):
    """H3C Comware 交换机配置解析器。"""

    template_name = "h3c_switch.ttp"

    def parse(self, raw_text: str) -> dict[str, Any]:
        """解析 H3C 交换机配置文本。

        Returns:
            包含 interfaces, vlans, vpn_instances 等键的字典
        """
        return _extract_ttp_result(self._run_ttp(raw_text))


@ParserFactory.register("H3C", "router")
class H3CRouterParser(BaseParser):
    """H3C Comware 路由器配置解析器。"""

    template_name = "h3c_router.ttp"

    def parse(self, raw_text: str) -> dict[str, Any]:
        """解析 H3C 路由器配置文本。

        Returns:
            包含 interfaces, vpn_instances, static_routes 等键的字典
        """
        return _extract_ttp_result(self._run_ttp(raw_text))
