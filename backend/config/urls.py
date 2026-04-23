from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def api_root(request):
    """用于快速检查 API 是否可达：访问 /api/ 返回 200"""
    return JsonResponse({'status': 'ok', 'message': 'API 正常'})

urlpatterns = [
    path('api/', api_root),
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.elders.urls')),
    path('api/communities/', include('apps.community.urls')),
    path('api/health/', include('apps.health.urls')),
    path('api/checkup/', include('apps.checkup.urls')),
    path('api/alerts/', include('apps.alerts.urls')),
    path('api/ai/', include('apps.ai.urls')),
    path('api/announcements/', include('apps.announcements.urls')),
    path('api/care/', include('apps.care.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
