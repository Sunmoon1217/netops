import json
from pathlib import Path

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_http_methods

from ops.parsers.factory import ParserFactory

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "parsers" / "templates"


@require_GET
def parser_list(request):
    """获取所有已注册的解析器列表"""
    parsers = []
    for (vendor, device_type), parser_cls in ParserFactory._registry.items():
        parsers.append(
            {
                "vendor": vendor,
                "device_type": device_type,
                "class_name": parser_cls.__name__,
                "template_name": parser_cls.template_name,
                "description": parser_cls.__doc__ or "",
            }
        )
    return JsonResponse({"parsers": parsers})


@require_GET
def parser_template_list(request):
    """获取所有模板文件列表"""
    templates = []
    for f in _TEMPLATES_DIR.glob("*.ttp"):
        templates.append({"name": f.name, "size": f.stat().st_size})
    return JsonResponse({"templates": templates})


@require_GET
def parser_template_detail(request, name):
    """获取模板文件内容"""
    path = _TEMPLATES_DIR / name
    if not path.exists():
        return JsonResponse({"error": f"模板不存在: {name}"}, status=404)
    return JsonResponse(
        {
            "name": name,
            "content": path.read_text(encoding="utf-8"),
            "size": path.stat().st_size,
        }
    )


@require_http_methods(["PUT"])
def parser_template_update(request, name):
    """更新模板文件内容"""
    path = _TEMPLATES_DIR / name
    if not path.exists():
        return JsonResponse({"error": f"模板不存在: {name}"}, status=404)
    try:
        data = json.loads(request.body)
        content = data.get("content", "")
        path.write_text(content, encoding="utf-8")
        return JsonResponse({"name": name, "size": path.stat().st_size, "message": "保存成功"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
