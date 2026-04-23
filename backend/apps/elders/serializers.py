from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Elder
from .utils import ensure_elder_profile

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """登录时校验：已停用社区的账号禁止登录"""

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        elder = ensure_elder_profile(user)
        if elder:
            from apps.community.models import Community
            community = Community.objects.filter(pk=elder.community_id).first()
            if community and not community.is_active:
                raise serializers.ValidationError(
                    {'detail': '该账号所属社区已停用，无法登录。如有疑问请联系管理员。'}
                )
        return data


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
    login_password = serializers.CharField(write_only=True, required=False, min_length=6, max_length=128,
                                          help_text='老人端登录密码（用户名=身份证号），留空则不创建/修改账号')

    class Meta:
        model = Elder
        fields = '__all__'

    def _ensure_user_for_elder(self, elder, password):
        if not password or not elder.id_card:
            return
        user, created = User.objects.get_or_create(
            username=elder.id_card,
            defaults={'name': elder.name, 'phone': elder.phone or '', 'role': 'elder', 'elder_profile': elder}
        )
        if user.elder_profile_id != elder.id:
            user.elder_profile = elder
            user.name = elder.name
            user.phone = elder.phone or ''
            user.save(update_fields=['elder_profile_id', 'name', 'phone'])
        user.set_password(password)
        user.save()

    def create(self, validated_data):
        login_password = validated_data.pop('login_password', None)
        elder = super().create(validated_data)
        self._ensure_user_for_elder(elder, login_password)
        return elder

    def update(self, instance, validated_data):
        login_password = validated_data.pop('login_password', None)
        elder = super().update(instance, validated_data)
        self._ensure_user_for_elder(elder, login_password)
        return elder

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


class ElderRegisterSerializer(serializers.Serializer):
    """老人端注册：选择社区 + 身份证 + 密码"""
    community_id = serializers.IntegerField()
    name = serializers.CharField(max_length=64)
    phone = serializers.CharField(max_length=20)
    id_card = serializers.CharField(max_length=18, min_length=15)
    password = serializers.CharField(min_length=6, write_only=True)

    def validate_name(self, v):
        v = (v or '').strip()
        if not v:
            raise serializers.ValidationError('姓名不能为空')
        return v

    def validate_id_card(self, v):
        v = (v or '').strip()
        if len(v) not in (15, 18):
            raise serializers.ValidationError('身份证长度不正确')
        return v

    def validate_phone(self, v):
        v = (v or '').strip()
        if not v:
            raise serializers.ValidationError('电话号码不能为空')
        # 简单校验：中国大陆手机号 11 位；如果你后面要支持座机/港澳台可放宽
        if v.isdigit() and len(v) == 11:
            return v
        # 允许包含 + - 空格 的国际号码形式
        ok_chars = set('0123456789+- ')
        if any(ch not in ok_chars for ch in v):
            raise serializers.ValidationError('电话号码格式不正确')
        return v

    def create(self, validated_data):
        from datetime import date
        from apps.community.models import Community

        community_id = validated_data['community_id']
        name = validated_data['name']
        phone = validated_data['phone']
        id_card = validated_data['id_card']
        password = validated_data['password']

        if User.objects.filter(username=id_card).exists():
            raise serializers.ValidationError({'id_card': '该身份证号已注册'})
        if Elder.objects.filter(id_card=id_card).exists():
            raise serializers.ValidationError({'id_card': '该身份证号已存在老人档案'})

        community = Community.objects.filter(id=community_id, is_active=True).first()
        if not community:
            raise serializers.ValidationError({'community_id': '社区不存在或已停用'})

        # 从身份证解析生日与性别（18位：YYYYMMDD + 第17位奇男偶女；15位按 19YY 处理）
        gender = 'M'
        birth = date(1950, 1, 1)
        try:
            if len(id_card) == 18:
                birth_str = id_card[6:14]
                birth = date(int(birth_str[0:4]), int(birth_str[4:6]), int(birth_str[6:8]))
                gender = 'M' if int(id_card[16]) % 2 == 1 else 'F'
            else:
                birth_str = '19' + id_card[6:12]
                birth = date(int(birth_str[0:4]), int(birth_str[4:6]), int(birth_str[6:8]))
                gender = 'M' if int(id_card[14]) % 2 == 1 else 'F'
        except Exception:
            # 解析失败使用默认值
            pass

        elder = Elder.objects.create(
            community=community,
            name=name,
            gender=gender,
            birth_date=birth,
            id_card=id_card,
            phone=phone,
            address='',
            emergency_contact='',
            emergency_phone='',
            medical_history='',
            notes='',
            is_active=True,
        )

        user = User(
            username=id_card,
            role='elder',
            name=name,
            phone=phone,
            elder_profile=elder,
        )
        user.set_password(password)
        user.save()
        return user
