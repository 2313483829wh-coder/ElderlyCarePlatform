from datetime import date
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import Checkup
from .serializers import CheckupSerializer
from apps.elders.models import Elder
from apps.elders.utils import ensure_elder_profile


class CheckupViewSet(viewsets.ModelViewSet):
    queryset = Checkup.objects.select_related('elder', 'elder__community').all()
    serializer_class = CheckupSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    filterset_fields = ['elder', 'year', 'sequence', 'elder__community']
    search_fields = ['elder__name']

    @action(detail=False, methods=['get'])
    def missing(self, request):
        """查找今年体检未完成（少于2次）的老人"""
        year = int(request.query_params.get('year', date.today().year))
        community_id = request.query_params.get('community')

        # 只查询在用社区的活跃老人
        elders = Elder.objects.filter(is_active=True, community__is_active=True)
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
        return Response(CheckupSerializer(records, many=True, context={'request': request}).data)

    @action(detail=False, methods=['get'], url_path='my')
    def my_checkups(self, request):
        """老人端：获取本人体检记录"""
        user = request.user
        elder = ensure_elder_profile(user)
        if not elder:
            return Response({'detail': '未关联老人档案'}, status=status.HTTP_400_BAD_REQUEST)
        records = Checkup.objects.filter(elder=elder)
        return Response(CheckupSerializer(records, many=True, context={'request': request}).data)

    @action(detail=False, methods=['post'], url_path='my-upload')
    def my_upload(self, request):
        """老人端：上传/替换体检报告（支持拍照上传）"""
        user = request.user
        elder = ensure_elder_profile(user)
        if not elder:
            return Response({'detail': '未关联老人档案'}, status=status.HTTP_400_BAD_REQUEST)

        report_file = request.FILES.get('report_file')
        if not report_file:
            return Response({'detail': '请上传体检报告文件'}, status=status.HTTP_400_BAD_REQUEST)

        checkup_id = request.data.get('checkup_id')
        if checkup_id:
            checkup = Checkup.objects.filter(id=checkup_id, elder=elder).first()
            if not checkup:
                return Response({'detail': '体检记录不存在'}, status=status.HTTP_404_NOT_FOUND)
        else:
            year = request.data.get('year')
            sequence = request.data.get('sequence')
            check_date = request.data.get('check_date')
            if not (year and sequence and check_date):
                return Response({'detail': '缺少 year/sequence/check_date'}, status=status.HTTP_400_BAD_REQUEST)
            checkup, _ = Checkup.objects.get_or_create(
                elder=elder,
                year=year,
                sequence=sequence,
                defaults={'check_date': check_date}
            )

        # 更新可编辑字段（允许老人补充基础描述）
        for field in ('hospital', 'overall_result', 'doctor_advice'):
            val = request.data.get(field)
            if val is not None:
                setattr(checkup, field, val)

        if request.data.get('check_date'):
            checkup.check_date = request.data.get('check_date')
        checkup.report_file = report_file
        checkup.save()

        return Response(CheckupSerializer(checkup, context={'request': request}).data)
