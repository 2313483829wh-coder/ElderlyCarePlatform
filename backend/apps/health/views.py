from datetime import date
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
from .models import DailyHealth
from .serializers import DailyHealthSerializer, HealthSubmitSerializer
from apps.alerts.models import Alert


class DailyHealthViewSet(viewsets.ModelViewSet):
    queryset = DailyHealth.objects.select_related('elder', 'elder__community').all()
    serializer_class = DailyHealthSerializer
    filterset_fields = ['elder', 'date', 'elder__community']
    ordering_fields = ['date', 'submitted_at']

    @action(detail=False, methods=['post'], url_path='submit')
    def submit_today(self, request):
        """老人端：提交今日健康数据"""
        user = request.user
        if not user.elder_profile:
            return Response({'detail': '未关联老人档案'}, status=status.HTTP_400_BAD_REQUEST)

        elder = user.elder_profile
        today = date.today()

        record, created = DailyHealth.objects.get_or_create(
            elder=elder, date=today,
            defaults=request.data,
        )
        if not created:
            for field, value in request.data.items():
                if hasattr(record, field) and value is not None:
                    setattr(record, field, value)
            record.save()

        anomalies = record.has_anomaly
        if anomalies:
            Alert.objects.get_or_create(
                elder=elder,
                alert_type='health',
                title=f'{elder.name} 今日健康数据异常',
                defaults={
                    'level': 'critical' if len(anomalies) >= 2 else 'warning',
                    'detail': f'异常项目: {", ".join(anomalies)}',
                },
            )

        return Response({
            'message': '提交成功',
            'anomalies': anomalies,
            'data': DailyHealthSerializer(record).data,
        })

    @action(detail=False, methods=['get'], url_path='today/(?P<community_id>[^/.]+)')
    def community_today(self, request, community_id=None):
        """获取某社区今日所有老人健康数据"""
        today = date.today()
        records = DailyHealth.objects.filter(
            elder__community_id=community_id, date=today
        ).select_related('elder')
        return Response(DailyHealthSerializer(records, many=True).data)

    @action(detail=False, methods=['get'], url_path='history/(?P<elder_id>[^/.]+)')
    def elder_history(self, request, elder_id=None):
        """获取某老人的健康数据历史"""
        records = DailyHealth.objects.filter(elder_id=elder_id).order_by('-date')[:30]
        return Response(DailyHealthSerializer(records, many=True).data)

    @action(detail=False, methods=['get'], url_path='my-history')
    def my_history(self, request):
        """老人端：查看自己的健康数据"""
        user = request.user
        if not user.elder_profile:
            return Response([])
        records = DailyHealth.objects.filter(elder=user.elder_profile).order_by('-date')[:30]
        return Response(DailyHealthSerializer(records, many=True).data)
