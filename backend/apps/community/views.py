from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from .models import Community
from .serializers import CommunitySerializer


class CommunityViewSet(viewsets.ModelViewSet):
    # 统计老人数量时只计算活跃老人
    queryset = Community.objects.annotate(
        elder_count=Count('elders', filter=Q(elders__is_active=True))
    )
    serializer_class = CommunitySerializer
    search_fields = ['name', 'address']
