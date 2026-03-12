from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny
from .models import Community
from .serializers import CommunitySerializer


class CommunityViewSet(viewsets.ModelViewSet):
    # 统计老人数量时只计算活跃老人
    queryset = Community.objects.annotate(
        elder_count=Count('elders', filter=Q(elders__is_active=True))
    )
    serializer_class = CommunitySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'address', 'contact_person']

    @action(detail=False, methods=['get'], url_path='public', permission_classes=[AllowAny])
    def public_list(self, request):
        """公开：注册用的社区列表（仅在用社区）"""
        qs = Community.objects.filter(is_active=True).order_by('created_at')
        data = [{'id': c.id, 'name': c.name} for c in qs]
        return Response(data)
