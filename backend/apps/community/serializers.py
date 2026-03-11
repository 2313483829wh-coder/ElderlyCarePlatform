from rest_framework import serializers
from .models import Community


class CommunitySerializer(serializers.ModelSerializer):
    elder_count = serializers.IntegerField(read_only=True)
    today_reported = serializers.SerializerMethodField()
    alert_count = serializers.SerializerMethodField()

    class Meta:
        model = Community
        fields = '__all__'

    def get_today_reported(self, obj):
        from datetime import date
        from apps.health.models import DailyHealth
        # 停用的社区不统计
        if not obj.is_active:
            return 0
        return DailyHealth.objects.filter(elder__community=obj, date=date.today()).count()

    def get_alert_count(self, obj):
        from datetime import date
        from apps.alerts.models import Alert
        # 停用的社区不统计
        if not obj.is_active:
            return 0
        # 只统计今天的健康异常预警
        return Alert.objects.filter(
            elder__community=obj, 
            status='pending',
            alert_type='health',
            created_at__date=date.today()
        ).count()
