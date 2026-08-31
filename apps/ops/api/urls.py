from django.urls import path

from . import configs, parsers

urlpatterns = [
    path("parsers/", parsers.parser_list, name="parser-list"),
    path("parsers/templates/", parsers.parser_template_list, name="parser-template-list"),
    path("parsers/templates/<str:name>/", parsers.parser_template_detail, name="parser-template-detail"),
    path("parsers/templates/<str:name>/update/", parsers.parser_template_update, name="parser-template-update"),
    path("configs/git-content/", configs.git_content, name="git-content"),
    path("configs/git-diff/", configs.git_diff, name="git-diff"),
    path("configs/history/", configs.config_history, name="config-history"),
    path("configs/devices/", configs.config_devices, name="config-devices"),
]
