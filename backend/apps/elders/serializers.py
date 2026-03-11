from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Elder

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'phone', 'role', 'elder_profile']
        read_only_fields = ['id']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'name', 'phone', 'role', 'elder_profile']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ElderSerializer(serializers.ModelSerializer):
    community_name = serializers.CharField(source='community.name', read_only=True)
    age = serializers.IntegerField(read_only=True)
    today_health = serializers.SerializerMethodField()
    checkup_status = serializers.SerializerMethodField()
    has_alert = serializers.SerializerMethodField()

    class Meta:
        model = Elder
        fields = '__all__'

    def get_today_health(self, obj):
        from datetime import date
        from apps.health.models import DailyHealth
        record = DailyHealth.objects.filter(elder=obj, date=date.today()).first()
        if not record:
            return None
        return {
            'heart_rate': record.heart_rate,
            'blood_oxygen': str(record.blood_oxygen) if record.blood_oxygen else None,
            'systolic_bp': record.systolic_bp,
            'diastolic_bp': record.diastolic_bp,
            'temperature': str(record.temperature) if record.temperature else None,
            'blood_sugar': str(record.blood_sugar) if record.blood_sugar else None,
            'feeling': record.feeling,
            'anomalies': record.has_anomaly,
        }

    def get_checkup_status(self, obj):
        """今年体检完成情况: 0/2, 1/2, 2/2"""
        from datetime import date
        year = date.today().year
        done = obj.checkups.filter(year=year).count()
        return {'year': year, 'done': done, 'required': 2, 'ok': done >= 2}

    def get_has_alert(self, obj):
        return obj.alerts.filter(status='pending').exists()


class ElderSimpleSerializer(serializers.ModelSerializer):
    """老人端用的简单序列化"""
    age = serializers.IntegerField(read_only=True)
    community_name = serializers.CharField(source='community.name', read_only=True)

    class Meta:
        model = Elder
        fields = ['id', 'name', 'gender', 'age', 'community_name', 'phone']
