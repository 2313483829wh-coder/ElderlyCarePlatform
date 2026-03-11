from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from .models import Community
from .serializers import CommunitySerializer


class CommunityViewSet(viewsets.ModelViewSet):
    queryset = Community.objects.annotate(elder_count=Count('elders'))
    serializer_class = CommunitySerializer
    search_fields = ['name', 'address']
