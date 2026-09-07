"""华为配置解析器 - 纯函数，无 Django 依赖。"""

from typing import Any

from .base import BaseParser
from .factory import ParserFactory


def _extract_ttp_result(result: list) -> dict[str, Any]:
    """从 TTP 原始结果中提取第一个匹配组的字典。"""
    if result and result[0]:
        return result[0][0]
    return {}


@ParserFactory.register("Huawei", "switch")
class HuaweiSwitchParser(BaseParser):
    """华为交换机配置解析器。"""

    template_name = "huawei_switch.ttp"

    def parse(self, raw_text: str) -> dict[str, Any]:
        """解析华为交换机配置文本。

        Returns:
            包含 interfaces, vlans, static_routes 等键的字典
        """
        return _extract_ttp_result(self._run_ttp(raw_text))
