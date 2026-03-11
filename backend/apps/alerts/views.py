from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Alert
from .serializers import AlertSerializer


class AlertViewSet(viewsets.ModelViewSet):
    # 默认只显示在用社区的预警
    queryset = Alert.objects.select_related('elder', 'elder__community').filter(elder__community__is_active=True)
    serializer_class = AlertSerializer
    filterset_fields = ['alert_type', 'level', 'status', 'elder', 'elder__community']
    search_fields = ['title', 'detail']

    @action(detail=True, methods=['put'])
    def resolve(self, request, pk=None):
        alert = self.get_object()
        alert.status = 'resolved'
        alert.resolved_at = timezone.now()
        alert.resolved_note = request.data.get('note', '')
        alert.save()
        return Response(AlertSerializer(alert).data)

    @action(detail=False, methods=['get'])
    def pending(self, request):
        community_id = request.query_params.get('community')
        # 只显示在用社区的预警
        qs = Alert.objects.filter(status='pending', elder__community__is_active=True)
        if community_id:
            qs = qs.filter(elder__community_id=community_id)
        return Response(AlertSerializer(qs, many=True).data)
