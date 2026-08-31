import re

from django.db import models


class SecurityZone(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="安全区名称")
    color = models.CharField(max_length=7, default="#3b82f6", verbose_name="标识颜色")
    description = models.TextField(blank=True, default="", verbose_name="描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "逻辑安全区"
        verbose_name_plural = verbose_name
        ordering = ("name",)

    def __str__(self):
        return self.name


class DataCenter(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="数据中心名称")
    address = models.CharField(max_length=255, blank=True, default="", verbose_name="地址")
    contact = models.CharField(max_length=100, blank=True, default="", verbose_name="联系人")
    phone = models.CharField(max_length=50, blank=True, default="", verbose_name="联系电话")
    remark = models.TextField(blank=True, default="", verbose_name="备注")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "数据中心"
        verbose_name_plural = verbose_name
        ordering = ("name",)

    def __str__(self):
        return self.name


class Room(models.Model):
    name = models.CharField(max_length=100, verbose_name="机房名称")
    datacenter = models.ForeignKey(
        DataCenter, on_delete=models.CASCADE, related_name="rooms", verbose_name="所属数据中心"
    )
    contact = models.CharField(max_length=100, blank=True, default="", verbose_name="联系人")
    remark = models.TextField(blank=True, default="", verbose_name="备注")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "机房"
        verbose_name_plural = verbose_name
        ordering = ("datacenter", "name")
        constraints = (models.UniqueConstraint(fields=["datacenter", "name"], name="uni_room_datacenter_name"),)

    def __str__(self):
        return f"{self.datacenter.name} / {self.name}"


class Cabinet(models.Model):
    STATUS_CHOICES = [
        ("active", "使用中"),
        ("reserved", "预留"),
        ("maintenance", "维护中"),
        ("decommissioned", "已下架"),
    ]

    name = models.CharField(max_length=50, verbose_name="机柜编号")
    row = models.CharField(max_length=20, blank=True, default="", verbose_name="排")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="cabinets", verbose_name="所属机房")
    total_u = models.PositiveIntegerField(default=42, verbose_name="总U数")
    power_capacity = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="额定功率(kW)"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active", verbose_name="状态")
    remark = models.TextField(blank=True, default="", verbose_name="备注")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "机柜"
        verbose_name_plural = verbose_name
        ordering = ("room", "row", "name")
        constraints = (models.UniqueConstraint(fields=["room", "name"], name="uni_cabinet_room_name"),)

    def __str__(self):
        return f"{self.room} / {self.name}"

    def save(self, *args, **kwargs):
        if not self.row and self.name:
            match = re.match(r"^([A-Za-z]+)", self.name)
            if match:
                self.row = match.group(1).upper()
        super().save(*args, **kwargs)


class Vendor(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="厂商名称")
    name_en = models.CharField(max_length=100, blank=True, default="", verbose_name="英文名")
    abbr = models.CharField(max_length=20, blank=True, default="", verbose_name="缩写")

    class Meta:
        verbose_name = "设备厂商"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class DeviceModel(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="设备型号")
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="device_models", verbose_name="所属厂商")

    class Meta:
        verbose_name = "设备型号"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.vendor.name} {self.name}"


class Device(models.Model):
    DEVICE_TYPE_CHOICES = (
        ("firewall", "防火墙"),
        ("switch", "交换机"),
        ("loadbalancer", "负载均衡"),
        ("router", "路由器"),
        ("server", "服务器"),
        ("dns", "域名解析"),
        ("dwdm", "波分复用"),
        ("internalac", "上网行为管理"),
        ("wirelessac", "无线控制器"),
    )

    hostname = models.CharField(max_length=100, unique=True, verbose_name="主机名")
    device_model = models.ForeignKey(
        DeviceModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="devices",
        verbose_name="设备型号",
    )
    device_type = models.CharField(max_length=50, choices=DEVICE_TYPE_CHOICES, verbose_name="设备类型")
    idc = models.ForeignKey(
        DataCenter,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="devices",
        verbose_name="数据中心",
    )
    cabinet = models.ForeignKey(
        Cabinet,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="devices",
        verbose_name="所属机柜",
    )
    security_zone = models.ForeignKey(
        SecurityZone,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="devices",
        verbose_name="安全区",
    )
    u_position = models.PositiveIntegerField(blank=True, null=True, verbose_name="起始U位")
    height = models.PositiveIntegerField(default=1, verbose_name="设备高度(U)")
    ip_address = models.CharField(max_length=50, blank=True, default="", verbose_name="管理IP")
    remark = models.TextField(blank=True, default="", verbose_name="备注")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "网络设备"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.hostname


class DeviceConnection(models.Model):
    CONNECTION_TYPE_CHOICES = (
        ("netmiko", "Netmiko"),
        ("napalm", "NAPALM"),
        ("paramiko", "Paramiko"),
        ("ssh", "SSH"),
    )

    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="connections",
        null=True,
        blank=True,
        verbose_name="关联设备",
    )
    address = models.GenericIPAddressField(blank=True, null=True, verbose_name="连接地址")
    connection_type = models.CharField(
        max_length=20, choices=CONNECTION_TYPE_CHOICES, default="napalm", verbose_name="连接类型"
    )
    driver = models.CharField(max_length=50, blank=True, default="", verbose_name="驱动/平台")
    port = models.PositiveIntegerField(default=22, verbose_name="端口")
    account_type = models.CharField(
        max_length=20,
        choices=[("admin", "管理员"), ("operator", "操作员"), ("readonly", "只读用户")],
        default="admin",
        verbose_name="账号类型",
    )
    username = models.CharField(max_length=100, verbose_name="用户名")
    password = models.CharField(max_length=255, verbose_name="密码")
    enable_password = models.CharField(max_length=255, blank=True, default="", verbose_name="Enable密码")
    timeout = models.PositiveIntegerField(default=30, verbose_name="连接超时(秒)")
    enabled = models.BooleanField(default=True, verbose_name="启用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "设备连接"
        verbose_name_plural = verbose_name
        constraints = (
            models.UniqueConstraint(fields=["device", "account_type"], name="uni_deviceconn_device_account"),
        )

    def __str__(self):
        return f"{self.device.hostname} ({self.connection_type})"


class DeviceConfig(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="configs", verbose_name="关联设备")
    git_commit_hash = models.CharField(max_length=40, verbose_name="Git Commit Hash")
    config_json = models.JSONField(blank=True, null=True, verbose_name="解析后的配置数据")
    parse_duration = models.FloatField(null=True, blank=True, verbose_name="解析耗时(秒)")
    collected_at = models.DateTimeField(auto_now_add=True, verbose_name="采集时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "设备配置"
        verbose_name_plural = verbose_name
        ordering = ("-collected_at",)

    def __str__(self):
        return f"{self.device.hostname} - {self.collected_at}"


class ConfigBase(models.Model):
    """配置模型基类"""

    device = models.ForeignKey(Device, on_delete=models.CASCADE, verbose_name="关联设备")
    is_active = models.BooleanField(default=True, verbose_name="是否生效")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        abstract = True


class Vlan(models.Model):
    """VLAN"""

    vid = models.PositiveIntegerField(unique=True, verbose_name="VLAN ID")
    name = models.CharField(max_length=100, blank=True, default="", verbose_name="VLAN名称")
    description = models.CharField(max_length=255, blank=True, default="", verbose_name="描述")

    class Meta:
        verbose_name = "VLAN"
        verbose_name_plural = verbose_name
        ordering = ("vid",)

    def __str__(self):
        return f"VLAN {self.vid}" + (f" ({self.name})" if self.name else "")


class Vrf(ConfigBase):
    """VRF"""

    name = models.CharField(max_length=255, verbose_name="名称")
    rd = models.CharField(max_length=50, blank=True, default="", verbose_name="RD")
    description = models.TextField(blank=True, default="", verbose_name="描述")

    class Meta:
        verbose_name = "VRF"
        verbose_name_plural = verbose_name
        constraints = (models.UniqueConstraint(fields=["device", "name"], name="uni_vrf_device_name"),)

    def __str__(self):
        return f"{self.device.hostname} / {self.name}"


class Interface(ConfigBase):
    """网络接口"""

    MODE_CHOICES = (
        ("layer3", "三层接口"),
        ("access", "Access"),
        ("hybrid", "Hybrid"),
        ("trunk", "Trunk"),
    )

    interface = models.CharField(max_length=255, verbose_name="接口名")
    description = models.CharField(max_length=255, null=True, verbose_name="描述")
    enabled = models.BooleanField(default=False, verbose_name="启用")
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, null=True, blank=True, verbose_name="接口模式")
    vlans = models.JSONField(default=dict, blank=True, verbose_name="VLAN配置")
    vrf = models.ForeignKey(
        Vrf, on_delete=models.SET_NULL, null=True, blank=True, related_name="interfaces", verbose_name="VRF"
    )
    type = models.CharField(max_length=255, null=True, verbose_name="接口类型")
    combo_type = models.CharField(max_length=255, null=True, verbose_name="Combo类型")
    ip_address = models.CharField(max_length=255, null=True, verbose_name="IP地址")
    subnet_mask = models.CharField(max_length=255, null=True, verbose_name="子网掩码")

    class Meta:
        verbose_name = "网络接口"
        verbose_name_plural = verbose_name
        constraints = (models.UniqueConstraint(fields=["device", "interface"], name="uni_device_interface"),)

    def __str__(self):
        return f"{self.device.hostname} / {self.interface}"


class DeviceAccount(ConfigBase):
    """设备管理用户（从配置解析）"""

    username = models.CharField(max_length=100, verbose_name="用户名")
    auth_type = models.CharField(
        max_length=20,
        choices=[
            ("password", "密码认证"),
            ("ssh-key", "SSH密钥"),
            ("both", "双因素认证"),
        ],
        default="password",
        verbose_name="认证方式",
    )
    privilege = models.CharField(
        max_length=20,
        choices=[
            ("admin", "管理员"),
            ("operator", "操作员"),
            ("readonly", "只读用户"),
        ],
        default="admin",
        verbose_name="权限级别",
    )
    enabled = models.BooleanField(default=True, verbose_name="启用")
    description = models.CharField(max_length=255, blank=True, default="", verbose_name="描述")

    class Meta:
        verbose_name = "设备账号"
        verbose_name_plural = verbose_name
        constraints = (
            models.UniqueConstraint(fields=["device", "username"], name="uni_deviceaccount_device_username"),
        )

    def __str__(self):
        return f"{self.device.hostname} / {self.username}"


class SnmpConfig(models.Model):
    """SNMP配置基线"""

    device = models.OneToOneField(Device, on_delete=models.CASCADE, related_name="snmp_config", verbose_name="关联设备")
    version = models.CharField(
        max_length=10, choices=[("v1", "v1"), ("v2c", "v2c"), ("v3", "v3")], default="v2c", verbose_name="SNMP版本"
    )
    community_read = models.CharField(max_length=100, blank=True, default="", verbose_name="读社区字符串")
    community_write = models.CharField(max_length=100, blank=True, default="", verbose_name="写社区字符串")
    port = models.PositiveIntegerField(default=161, verbose_name="监听端口")
    trap_enabled = models.BooleanField(default=False, verbose_name="启用Trap")
    trap_server = models.GenericIPAddressField(blank=True, null=True, verbose_name="Trap服务器")
    trap_port = models.PositiveIntegerField(default=162, verbose_name="Trap端口")
    enabled = models.BooleanField(default=True, verbose_name="启用SNMP")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "SNMP配置"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.device.hostname} SNMP"


class NtpConfig(models.Model):
    """NTP配置基线"""

    device = models.OneToOneField(Device, on_delete=models.CASCADE, related_name="ntp_config", verbose_name="关联设备")
    server1 = models.GenericIPAddressField(verbose_name="NTP服务器1")
    server2 = models.GenericIPAddressField(blank=True, null=True, verbose_name="NTP服务器2")
    server3 = models.GenericIPAddressField(blank=True, null=True, verbose_name="NTP服务器3")
    timezone = models.CharField(max_length=50, default="UTC", verbose_name="时区")
    sync_interval = models.PositiveIntegerField(default=64, verbose_name="同步间隔(秒)")
    enabled = models.BooleanField(default=True, verbose_name="启用NTP")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "NTP配置"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.device.hostname} NTP"


class SyslogConfig(models.Model):
    """Syslog配置基线"""

    device = models.OneToOneField(
        Device, on_delete=models.CASCADE, related_name="syslog_config", verbose_name="关联设备"
    )
    server1 = models.GenericIPAddressField(verbose_name="日志服务器1")
    server2 = models.GenericIPAddressField(blank=True, null=True, verbose_name="日志服务器2")
    port = models.PositiveIntegerField(default=514, verbose_name="端口")
    facility = models.CharField(
        max_length=20,
        choices=[(f"local{i}", f"local{i}") for i in range(8)],
        default="local7",
        verbose_name="Facility",
    )
    level = models.CharField(
        max_length=20,
        choices=[
            ("emergency", "emergency"),
            ("alert", "alert"),
            ("critical", "critical"),
            ("error", "error"),
            ("warning", "warning"),
            ("notice", "notice"),
            ("informational", "informational"),
            ("debugging", "debugging"),
        ],
        default="informational",
        verbose_name="日志级别",
    )
    enabled = models.BooleanField(default=True, verbose_name="启用Syslog")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "Syslog配置"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.device.hostname} Syslog"
