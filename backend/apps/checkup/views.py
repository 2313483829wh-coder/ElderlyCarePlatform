from datetime import date
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Checkup
from .serializers import CheckupSerializer
from apps.elders.models import Elder


class CheckupViewSet(viewsets.ModelViewSet):
    queryset = Checkup.objects.select_related('elder', 'elder__community').all()
    serializer_class = CheckupSerializer
    filterset_fields = ['elder', 'year', 'sequence', 'elder__community']
    search_fields = ['elder__name']

    @action(detail=False, methods=['get'])
    def missing(self, request):
        """查找今年体检未完成（少于2次）的老人"""
        year = int(request.query_params.get('year', date.today().year))
        community_id = request.query_params.get('community')

        elders = Elder.objects.filter(is_active=True)
        if community_id:
            elders = elders.filter(community_id=community_id)

        result = []
        for elder in elders.select_related('community'):
            done = elder.checkups.filter(year=year).count()
            if done < 2:
                result.append({
                    'elder_id': elder.id,
                    'elder_name': elder.name,
                    'community_name': elder.community.name,
                    'year': year,
                    'done': done,
                    'missing': 2 - done,
                })
        return Response(result)

    @action(detail=False, methods=['get'], url_path='elder/(?P<elder_id>[^/.]+)')
    def by_elder(self, request, elder_id=None):
        """查看某老人的所有体检记录"""
        records = Checkup.objects.filter(elder_id=elder_id)
        return Response(CheckupSerializer(records, many=True).data)
