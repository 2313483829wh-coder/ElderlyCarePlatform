from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .models import Elder
from .utils import ensure_elder_profile
from .serializers import (
    ElderSerializer, ElderSimpleSerializer,
    UserSerializer, UserCreateSerializer,
    ElderRegisterSerializer,
    CustomTokenObtainPairSerializer,
)

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """登录接口：已停用社区账号会在此被拦截并返回提示"""
    serializer_class = CustomTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    search_fields = ['username', 'name', 'phone']

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        ensure_elder_profile(request.user)
        ser = UserSerializer(request.user)
        return Response(ser.data)

    def _ensure_elder_profile(self, user):
        return ensure_elder_profile(user)

    @action(detail=False, methods=['patch'], url_path='update-phone')
    def update_phone(self, request):
        """老人端：修改当前用户手机号"""
        phone = (request.data.get('phone') or '').strip()
        if not phone:
            return Response({'phone': ['手机号不能为空']}, status=status.HTTP_400_BAD_REQUEST)
        if len(phone) != 11 or not phone.isdigit():
            return Response({'phone': ['请输入正确的11位手机号']}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        user.phone = phone
        user.save()
        elder = self._ensure_elder_profile(user)
        if elder:
            elder.phone = phone
            elder.save(update_fields=['phone'])
        return Response({'message': '修改成功', 'phone': phone})

    @action(detail=False, methods=['post'], url_path='change-password')
    def change_password(self, request):
        """已登录用户修改密码：需提供旧密码和新密码"""
        old_password = request.data.get('old_password') or ''
        new_password = request.data.get('new_password') or ''
        if not old_password:
            return Response({'old_password': ['请输入旧密码']}, status=status.HTTP_400_BAD_REQUEST)
        if not new_password or len(new_password) < 6:
            return Response({'new_password': ['新密码至少6位']}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        if not user.check_password(old_password):
            return Response({'old_password': ['旧密码错误']}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save(update_fields=['password'])
        return Response({'message': '密码修改成功，请重新登录'})

    @action(detail=False, methods=['post'], permission_classes=[AllowAny], url_path='elder-register')
    def elder_register(self, request):
        """老人端：注册（社区 + 身份证 + 密码）"""
        ser = ElderRegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        return Response({'message': '注册成功', 'username': user.username}, status=status.HTTP_201_CREATED)


class ElderViewSet(viewsets.ModelViewSet):
    queryset = Elder.objects.select_related('community').all()
    serializer_class = ElderSerializer
    search_fields = ['name', 'id_card', 'phone']
    filterset_fields = ['community', 'is_active']

    def update(self, request, *args, **kwargs):
        """支持部分更新老人信息"""
        partial = True  # 允许部分更新
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-community/(?P<community_id>[^/.]+)')
    def by_community(self, request, community_id=None):
        """获取某个社区下所有老人（带今日健康数据和预警标记）"""
        elders = Elder.objects.filter(
            community_id=community_id
        ).select_related('community')
        serializer = self.get_serializer(elders, many=True)
        return Response(serializer.data)
