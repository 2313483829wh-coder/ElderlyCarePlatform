from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .models import Elder
from .serializers import (
    ElderSerializer, ElderSimpleSerializer,
    UserSerializer, UserCreateSerializer,
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    search_fields = ['username', 'name', 'phone']

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        ser = UserSerializer(request.user)
        return Response(ser.data)


class ElderViewSet(viewsets.ModelViewSet):
    queryset = Elder.objects.select_related('community').all()
    serializer_class = ElderSerializer
    search_fields = ['name', 'id_card', 'phone']
    filterset_fields = ['community', 'is_active']

    @action(detail=False, methods=['get'], url_path='by-community/(?P<community_id>[^/.]+)')
    def by_community(self, request, community_id=None):
        """获取某个社区下所有老人（带今日健康数据和预警标记）"""
        elders = Elder.objects.filter(
            community_id=community_id, is_active=True
        ).select_related('community')
        serializer = self.get_serializer(elders, many=True)
        return Response(serializer.data)
