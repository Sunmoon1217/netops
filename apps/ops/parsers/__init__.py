# 导入厂商解析器以触发 @ParserFactory.register 装饰器
from .vendor import a10, cisco, f5, h3c, hillstone, huawei

__all__ = ["a10", "cisco", "f5", "h3c", "hillstone", "huawei"]
