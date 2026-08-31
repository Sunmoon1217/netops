from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("core.api.urls")),
    path("api/", include("assets.api.urls")),
    path("favicon.ico", views.favicon),
    # 前端静态资源
    re_path(r"^assets/(?P<path>.*)$", views.serve_frontend_assets),
]

# Vue SPA catch-all（必须放最后）
urlpatterns += [
    re_path(r"^(?!admin/|api/|static/|assets/|media/).*$", views.vue_index),
]

# DEBUG 模式下提供 Django 静态文件
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
