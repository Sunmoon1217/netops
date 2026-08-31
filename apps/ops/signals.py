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
        raw_text = instance.config_json
        if not raw_text:
            logger.info("DeviceConfig %s config_json 为空，跳过解析", instance.pk)
            return

        # 获取解析器并执行解析
        from ops.parsers.factory import ParserFactory

        try:
            parser = ParserFactory.get_parser(device)
        except ValueError as e:
            logger.warning("设备 %s 无匹配解析器: %s", device.hostname, e)
            return

        if isinstance(raw_text, dict):
            raw_text = str(raw_text)

        result = parser.parse(raw_text)

        # 更新 DeviceConfig 的解析结果
        instance.config_json = result
        instance.save(update_fields=["config_json", "updated_at"])
        logger.info("设备 %s 配置解析完成", device.hostname)
    except Exception as e:
        logger.error("DeviceConfig %s 解析失败: %s", instance.pk, e, exc_info=True)
    finally:
        _processing.discard(instance.pk)
