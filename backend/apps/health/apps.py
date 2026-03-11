from django.apps import AppConfig


class HealthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.health'
    verbose_name = '每日健康'
