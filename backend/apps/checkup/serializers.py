from rest_framework import serializers
from .models import Checkup


class CheckupSerializer(serializers.ModelSerializer):
    elder_name = serializers.CharField(source='elder.name', read_only=True)
    community_name = serializers.CharField(source='elder.community.name', read_only=True)
    blood_pressure = serializers.SerializerMethodField() # 新增用于前端展示
    report_file_url = serializers.SerializerMethodField()

    class Meta:
        model = Checkup
        fields = '__all__'

    def get_blood_pressure(self, obj):
        if obj.systolic_bp and obj.diastolic_bp:
            return f'{obj.systolic_bp}/{obj.diastolic_bp}'
        return ''

    def get_report_file_url(self, obj):
        if not obj.report_file:
            return ''
        request = self.context.get('request')
        url = obj.report_file.url
        return request.build_absolute_uri(url) if request else url


class CheckupMissingSerializer(serializers.Serializer):
    """体检缺失提醒"""
    elder_id = serializers.IntegerField()
    elder_name = serializers.CharField()
    community_name = serializers.CharField()
    year = serializers.IntegerField()
    done = serializers.IntegerField()
    missing = serializers.IntegerField()
