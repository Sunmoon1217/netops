from django.urls import path

from . import parsers

urlpatterns = [
    path("parsers/", parsers.parser_list, name="parser-list"),
    path("parsers/templates/", parsers.parser_template_list, name="parser-template-list"),
    path("parsers/templates/<str:name>/", parsers.parser_template_detail, name="parser-template-detail"),
    path("parsers/templates/<str:name>/update/", parsers.parser_template_update, name="parser-template-update"),
]
