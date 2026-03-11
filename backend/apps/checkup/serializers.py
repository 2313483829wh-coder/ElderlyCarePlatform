from rest_framework import serializers
from .models import Checkup


class CheckupSerializer(serializers.ModelSerializer):
    elder_name = serializers.CharField(source='elder.name', read_only=True)
    community_name = serializers.CharField(source='elder.community.name', read_only=True)

    class Meta:
        model = Checkup
        fields = '__all__'


class CheckupMissingSerializer(serializers.Serializer):
    """体检缺失提醒"""
    elder_id = serializers.IntegerField()
    elder_name = serializers.CharField()
    community_name = serializers.CharField()
    year = serializers.IntegerField()
    done = serializers.IntegerField()
    missing = serializers.IntegerField()
