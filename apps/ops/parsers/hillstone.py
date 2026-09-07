"""山石配置解析器 - 纯函数，无 Django 依赖。"""

from typing import Any

from .base import BaseParser
from .factory import ParserFactory


def _extract_ttp_result(result: list) -> dict[str, Any]:
    """从 TTP 原始结果中提取第一个匹配组的字典。"""
    if result and result[0]:
        return result[0][0]
    return {}


@ParserFactory.register("Hillstone", "firewall")
class HillstoneFWParser(BaseParser):
    """山石防火墙配置解析器。"""

    template_name = "hillstone_fw.ttp"

    def parse(self, raw_text: str) -> dict[str, Any]:
        """解析山石防火墙配置文本。

        Returns:
            包含 interfaces, zones, rules, addresses 等键的字典
        """
        return _extract_ttp_result(self._run_ttp(raw_text))
