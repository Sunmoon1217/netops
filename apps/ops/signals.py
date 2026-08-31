import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)

_processing = set()


@receiver(post_save, sender="assets.DeviceConfig")
def on_device_config_saved(sender, instance, created, **kwargs):
    """DeviceConfig 保存后触发配置解析"""
    if not created:
        return
    if instance.pk in _processing:
        return

    _processing.add(instance.pk)
    try:
        device = instance.device
        hostname = device.hostname
        commit_hash = instance.git_commit_hash

        # 从 Git 仓库读取配置原文
        from ops.config_repo import get_config

        raw_text = get_config(hostname, commit_hash)
        if not raw_text:
            logger.warning("DeviceConfig %s: Git 仓库中无配置 (hostname=%s, hash=%s)",
                           instance.pk, hostname, commit_hash[:8] if commit_hash else "None")
            return

        # 获取解析器并执行解析
        from ops.parsers.factory import ParserFactory

        try:
            parser = ParserFactory.get_parser(device)
        except ValueError as e:
            logger.warning("设备 %s 无匹配解析器: %s", hostname, e)
            return

        result = parser.parse(raw_text)

        # 更新 DeviceConfig 的解析结果
        instance.config_json = result
        instance.save(update_fields=["config_json", "updated_at"])
        logger.info("设备 %s 配置解析完成 (hash=%s)", hostname, commit_hash[:8] if commit_hash else "None")
    except Exception as e:
        logger.error("DeviceConfig %s 解析失败: %s", instance.pk, e, exc_info=True)
    finally:
        _processing.discard(instance.pk)
