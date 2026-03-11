from rest_framework import serializers
from .models import DailyHealth


class DailyHealthSerializer(serializers.ModelSerializer):
    elder_name = serializers.CharField(source='elder.name', read_only=True)
    anomalies = serializers.SerializerMethodField()

    class Meta:
        model = DailyHealth
        fields = '__all__'

    def get_anomalies(self, obj):
        return obj.has_anomaly


class HealthSubmitSerializer(serializers.ModelSerializer):
    """老人端提交用"""
    class Meta:
        model = DailyHealth
        fields = ['heart_rate', 'blood_oxygen', 'systolic_bp', 'diastolic_bp',
                  'temperature', 'blood_sugar', 'weight', 'feeling']
