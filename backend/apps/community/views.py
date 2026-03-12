from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
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
