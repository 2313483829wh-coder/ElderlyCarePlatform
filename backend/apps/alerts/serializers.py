from rest_framework import serializers
from .models import Alert


class AlertSerializer(serializers.ModelSerializer):
    elder_name = serializers.CharField(source='elder.name', read_only=True)
    community_name = serializers.CharField(source='elder.community.name', read_only=True)
    type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Alert
        fields = '__all__'
