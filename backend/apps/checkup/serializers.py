from rest_framework import serializers
from .models import Checkup


class CheckupSerializer(serializers.ModelSerializer):
    elder_name = serializers.CharField(source='elder.name', read_only=True)
    community_name = serializers.CharField(source='elder.community.name', read_only=True)
    blood_pressure = serializers.SerializerMethodField() # 新增用于前端展示

    class Meta:
        model = Checkup
        fields = '__all__'

    def get_blood_pressure(self, obj):
        if obj.systolic_bp and obj.diastolic_bp:
            return f'{obj.systolic_bp}/{obj.diastolic_bp}'
        return ''


class CheckupMissingSerializer(serializers.Serializer):
    """体检缺失提醒"""
    elder_id = serializers.IntegerField()
    elder_name = serializers.CharField()
    community_name = serializers.CharField()
    year = serializers.IntegerField()
    done = serializers.IntegerField()
    missing = serializers.IntegerField()
