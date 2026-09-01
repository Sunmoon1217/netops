"""信号处理

1. DeviceConfig post_save → 解析 + Saver
2. Stage post_save → 触发下一阶段 Celery 任务
"""
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)

_processing = set()
_processing_stage = set()


# ---------------------------------------------------------------------------
# Stage 阶段联动
# ---------------------------------------------------------------------------

def _trigger_next_stage(task, stage_type, input_data=None):
    """创建并触发下一阶段"""
    from core.models import Stage
    from ops.tasks import run_collection_stage, run_parsing_stage, run_storage_stage

    task_map = {
        "collection": run_collection_stage,
        "parsing": run_parsing_stage,
        "storage": run_storage_stage,
    }

    next_stage = Stage.objects.create(
        task=task, stage_type=stage_type, status="running", input_data=input_data or {},
    )

    task_func = task_map.get(stage_type)
    if task_func:
        task_func.delay(next_stage.pk)

    logger.info("Triggered %s stage (id=%s) for task %s", stage_type, next_stage.pk, task.pk)


@receiver(post_save, sender="core.Stage")
def on_stage_complete(sender, instance, **kwargs):
    """Stage 完成后触发下一阶段"""
    if instance.status != "success":
        return
    if instance.pk in _processing_stage:
        return

    _processing_stage.add(instance.pk)
    try:
        from core.models import Task
        task = instance.task

        if instance.stage_type == "collection":
            _trigger_next_stage(task, "parsing")
        elif instance.stage_type == "parsing":
            _trigger_next_stage(task, "storage")
        elif instance.stage_type == "storage":
            Task.objects.filter(id=task.pk).update(
                status="success", result={"message": "All stages completed successfully"},
            )
    finally:
        _processing_stage.discard(instance.pk)


# ---------------------------------------------------------------------------
# DeviceConfig post_save
# ---------------------------------------------------------------------------

@receiver(post_save, sender="assets.DeviceConfig")
def on_device_config_saved(sender, instance, created, **kwargs):
    """DeviceConfig 保存后触发解析"""
    if not created or instance.pk in _processing:
        return

    _processing.add(instance.pk)
    try:
        device = instance.device
        hostname = device.hostname
        commit_hash = instance.git_commit_hash

        # 如果 config_json 为空，从 Git 读取并解析
        config_json = instance.config_json
        if not config_json or config_json == {}:
            from ops.config_repo import get_config
            from ops.parsers.factory import ParserFactory

            raw_text = get_config(hostname, commit_hash)
            if not raw_text:
                logger.warning("DeviceConfig %s: Git 无配置 (hash=%s)", instance.pk,
                               commit_hash[:8] if commit_hash else "None")
                return

            try:
                parser = ParserFactory.get_parser(device)
            except ValueError as e:
                logger.warning("设备 %s 无匹配解析器: %s", hostname, e)
                return

            config_json = parser.parse(raw_text)
            instance.config_json = config_json
            instance.save(update_fields=["config_json", "updated_at"])
            logger.info("设备 %s 配置解析完成", hostname)

        # config_json 有数据 → 分发到 Saver
        if config_json and config_json != {}:
            from ops.savers.registry import get_savers_for_config

            savers = get_savers_for_config(device.device_type, config_json)
            for key, saver in savers:
                try:
                    data = config_json.get(key)
                    if data:
                        created_n, updated_n = saver.save(device, {key: data})
                        logger.info("设备 %s [%s] 保存完成: +%d ~%d",
                                    hostname, key, created_n, updated_n)
                except Exception as e:
                    logger.error("设备 %s [%s] 保存失败: %s", hostname, key, e, exc_info=True)

    except Exception as e:
        logger.error("DeviceConfig %s 处理失败: %s", instance.pk, e, exc_info=True)
    finally:
        _processing.discard(instance.pk)
