from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.elders.urls')),
    path('api/communities/', include('apps.community.urls')),
    path('api/health/', include('apps.health.urls')),
    path('api/checkup/', include('apps.checkup.urls')),
    path('api/alerts/', include('apps.alerts.urls')),
    path('api/ai/', include('apps.ai.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
