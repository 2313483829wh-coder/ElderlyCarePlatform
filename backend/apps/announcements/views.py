from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Announcement
from .serializers import AnnouncementSerializer


class AnnouncementViewSet(viewsets.ModelViewSet):
    serializer_class = AnnouncementSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active', 'is_pinned', 'audience']
    search_fields = ['title', 'summary', 'content']
    ordering_fields = ['publish_at', 'created_at', 'updated_at']
    ordering = ['-is_pinned', '-publish_at', '-created_at']
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def get_queryset(self):
        queryset = Announcement.objects.all()
        if self.action == 'mobile_list':
            now = timezone.now()
            return queryset.filter(
                Q(is_active=True, publish_at__lte=now) |
                Q(is_active=True, publish_at__isnull=True)
            )
        return queryset

    def get_permissions(self):
        if self.action == 'mobile_list':
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['get'], url_path='mobile', permission_classes=[AllowAny])
    def mobile_list(self, request):
        queryset = self.filter_queryset(self.get_queryset()).order_by('-is_pinned', '-publish_at', '-created_at')
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
