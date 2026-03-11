from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Alert
from .serializers import AlertSerializer


class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.select_related('elder', 'elder__community').all()
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
        qs = Alert.objects.filter(status='pending')
        if community_id:
            qs = qs.filter(elder__community_id=community_id)
        return Response(AlertSerializer(qs, many=True).data)
