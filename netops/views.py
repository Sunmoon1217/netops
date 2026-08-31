from pathlib import Path

from django.http import HttpResponse, JsonResponse

FRONTEND = Path(__file__).resolve().parent.parent / "frontend" / "dist"


def vue_index(request):
    """返回 Vue 构建的 index.html"""
    index_path = FRONTEND / "index.html"
    if index_path.exists():
        return HttpResponse(index_path.read_bytes(), content_type="text/html")
    return JsonResponse({"error": "Index.html not found"}, status=404)


def favicon(request):
    """返回 favicon.ico"""
    favicon_path = FRONTEND / "favicon.ico"
    if favicon_path.exists():
        return HttpResponse(favicon_path.read_bytes(), content_type="image/x-icon")
    return HttpResponse(status=404)


def serve_frontend_assets(request, path):
    """服务 frontend/dist/assets/ 下的静态资源"""
    file_path = FRONTEND / "assets" / path
    if file_path.exists() and file_path.is_file():
        content_type = "application/javascript" if path.endswith(".js") else \
                       "text/css" if path.endswith(".css") else \
                       "image/svg+xml" if path.endswith(".svg") else \
                       "application/octet-stream"
        return HttpResponse(file_path.read_bytes(), content_type=content_type)
    return JsonResponse({"error": "Not found"}, status=404)
