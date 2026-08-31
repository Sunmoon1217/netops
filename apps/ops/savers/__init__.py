"""数据持久化 Saver 层

导入所有 Saver 模块，__init_subclass__ 自动完成注册。
新增 Saver 步骤：
1. 创建 xxx_saver.py
2. 定义 device_types 和 keys 类属性
3. 在本文件中 import
"""
from .base import BaseSaver
from .firewall import AddressBookSaver, PolicySaver, ServiceSaver
from .interface import InterfaceSaver
from .lb import GTMWideipSaver, LBPoolSaver, LBSnatSaver, LBVirtualServerSaver
from .registry import get_savers_for_config
from .routing import VrfSaver

__all__ = [
    "BaseSaver",
    "InterfaceSaver",
    "AddressBookSaver", "ServiceSaver", "PolicySaver",
    "LBVirtualServerSaver", "LBPoolSaver", "LBSnatSaver", "GTMWideipSaver",
    "VrfSaver",
    "get_savers_for_config",
]
