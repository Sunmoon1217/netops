from django.apps import AppConfig


class OperatorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ops"
    label = "operator"
    verbose_name = "运维操作"

    def ready(self):
        import ops.signals  # noqa: F401
