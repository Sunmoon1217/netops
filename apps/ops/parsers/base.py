from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

_TMPLS_DIR = Path(__file__).resolve().parent / "tmpls"


def _get_template_path(template_name: str) -> str:
    """在 tmpls/configs 和 tmpls/running 中查找模板"""
    for subdir in ("configs", "running"):
        path = _TMPLS_DIR / subdir / template_name
        if path.exists():
            return path.as_posix()
    raise FileNotFoundError(f"模板文件不存在: {template_name}")


class BaseParser(ABC):
    """解析器基类，纯函数，无 Django 依赖"""

    template_name: str = ""

    @abstractmethod
    def parse(self, raw_text: str) -> dict[str, Any]:
        """解析原始配置文本，返回结构化数据"""

    def _run_ttp(self, raw_text: str) -> Any:
        from ttp import ttp

        template_path = _get_template_path(self.template_name)
        parser = ttp(data=raw_text, template=template_path)
        parser.parse()
        return parser.result(format="raw")
