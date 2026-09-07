"""F5 配置解析器 - 纯函数，无 Django 依赖。"""

from typing import Any

from .base import BaseParser
from .factory import ParserFactory


def _extract_ttp_result(result: list) -> dict[str, Any]:
    """从 TTP 原始结果中提取第一个匹配组的字典。"""
    if result and result[0]:
        return result[0][0]
    return {}


@ParserFactory.register("F5", "loadbalancer")
class F5GTMParser(BaseParser):
    """F5 GTM (DNS) 负载均衡配置解析器。"""

    template_name = "f5_gtm.ttp"

    def parse(self, raw_text: str) -> dict[str, Any]:
        """解析 F5 GTM 配置文本。

        Returns:
            包含 datacenters, servers, pools, wideips 等键的字典
        """
        return _extract_ttp_result(self._run_ttp(raw_text))


@ParserFactory.register("F5", "loadbalancer_ltm")
class F5LTMParser(BaseParser):
    """F5 LTM (Local Traffic Manager) 负载均衡配置解析器。"""

    template_name = "f5_ltm.ttp"

    def parse(self, raw_text: str) -> dict[str, Any]:
        """解析 F5 LTM 配置文本。

        Returns:
            包含 nodes, pools, virtuals 等键的字典
        """
        return _extract_ttp_result(self._run_ttp(raw_text))
