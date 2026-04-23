from django.db.models import Count
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.elders.utils import ensure_elder_profile

from .models import (
    ActivityRegistration,
    CommunityActivity,
    FamilyContact,
    MedicationPlan,
    ServiceOrder,
)
from .serializers import (
    ActivityRegistrationSerializer,
    CommunityActivitySerializer,
    FamilyContactSerializer,
    MedicationPlanSerializer,
    ServiceOrderCreateSerializer,
    ServiceOrderSerializer,
)


class FamilyContactViewSet(viewsets.ModelViewSet):
    queryset = FamilyContact.objects.select_related('elder', 'elder__community').all()
    serializer_class = FamilyContactSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['elder', 'elder__community', 'relation', 'is_primary']
    search_fields = ['name', 'phone', 'elder__name']

    @action(detail=False, methods=['get'], url_path='my')
    def my_contacts(self, request):
        elder = ensure_elder_profile(request.user)
        if not elder:
            return Response({'detail': '未关联老人档案'}, status=status.HTTP_400_BAD_REQUEST)
        queryset = self.get_queryset().filter(elder=elder)
        return Response(self.get_serializer(queryset, many=True).data)


class MedicationPlanViewSet(viewsets.ModelViewSet):
    queryset = MedicationPlan.objects.select_related('elder', 'elder__community').all()
    serializer_class = MedicationPlanSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['elder', 'elder__community', 'is_active']
    search_fields = ['medicine_name', 'elder__name']

    @action(detail=False, methods=['get'], url_path='my')
    def my_plans(self, request):
        elder = ensure_elder_profile(request.user)
        if not elder:
            return Response({'detail': '未关联老人档案'}, status=status.HTTP_400_BAD_REQUEST)
        queryset = self.get_queryset().filter(elder=elder, is_active=True)
        return Response(self.get_serializer(queryset, many=True).data)

    @action(detail=True, methods=['post'], url_path='mark-taken')
    def mark_taken(self, request, pk=None):
        plan = self.get_object()
        if plan.last_taken_at and timezone.localtime(plan.last_taken_at).date() == timezone.localdate():
            return Response({'detail': '今天已经记录过服药了'}, status=status.HTTP_400_BAD_REQUEST)
        plan.last_taken_at = timezone.now()
        plan.save(update_fields=['last_taken_at'])
        return Response({'message': '已记录服药时间', 'last_taken_at': plan.last_taken_at})


class CommunityActivityViewSet(viewsets.ModelViewSet):
    queryset = CommunityActivity.objects.annotate(
        registration_count_value=Count('registrations')
    ).all()
    serializer_class = CommunityActivitySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['title', 'summary', 'content', 'location']
    ordering_fields = ['starts_at', 'created_at']
    ordering = ['-starts_at']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        try:
            elder = ensure_elder_profile(self.request.user)
        except Exception:
            elder = None
        context['elder'] = elder
        return context

    @action(detail=True, methods=['get'], url_path='registrations')
    def registrations(self, request, pk=None):
        activity = self.get_object()
        queryset = activity.registrations.select_related('elder')
        return Response(ActivityRegistrationSerializer(queryset, many=True).data)

    @action(detail=False, methods=['get'], url_path='mobile-list')
    def mobile_list(self, request):
        elder = ensure_elder_profile(request.user)
        if not elder:
            return Response({'detail': '未关联老人档案'}, status=status.HTTP_400_BAD_REQUEST)
        queryset = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True, context={**self.get_serializer_context(), 'elder': elder})
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        elder = ensure_elder_profile(request.user)
        if not elder:
            return Response({'detail': '未关联老人档案'}, status=status.HTTP_400_BAD_REQUEST)
        activity_id = request.data.get('activity_id')
        if not activity_id:
            return Response({'detail': '缺少活动ID'}, status=status.HTTP_400_BAD_REQUEST)
        activity = CommunityActivity.objects.filter(id=activity_id, is_active=True).first()
        if not activity:
            return Response({'detail': '活动不存在或已停用'}, status=status.HTTP_404_NOT_FOUND)
        registration, created = ActivityRegistration.objects.get_or_create(
            activity=activity,
            elder=elder,
            defaults={'status': 'registered'}
        )
        if not created and registration.status == 'registered':
            return Response({'detail': '你已经报名过该活动'}, status=status.HTTP_400_BAD_REQUEST)
        if activity.max_participants and activity.registrations.filter(status='registered').exclude(id=registration.id).count() >= activity.max_participants:
            return Response({'detail': '活动名额已满'}, status=status.HTTP_400_BAD_REQUEST)
        registration.status = 'registered'
        registration.notes = request.data.get('notes', registration.notes or '')
        registration.save()
        return Response(ActivityRegistrationSerializer(registration).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='cancel-registration')
    def cancel_registration(self, request):
        elder = ensure_elder_profile(request.user)
        if not elder:
            return Response({'detail': '未关联老人档案'}, status=status.HTTP_400_BAD_REQUEST)
        activity_id = request.data.get('activity_id')
        registration = ActivityRegistration.objects.filter(activity_id=activity_id, elder=elder, status='registered').first()
        if not registration:
            return Response({'detail': '未找到有效报名记录'}, status=status.HTTP_404_NOT_FOUND)
        registration.status = 'cancelled'
        registration.save(update_fields=['status'])
        return Response({'message': '已取消报名'})


class ServiceOrderViewSet(viewsets.ModelViewSet):
    queryset = ServiceOrder.objects.select_related('elder', 'community').all()
    serializer_class = ServiceOrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['request_type', 'service_kind', 'status', 'urgency', 'community', 'elder']
    search_fields = ['title', 'description', 'elder__name', 'contact_phone']
    ordering_fields = ['created_at', 'updated_at', 'resolved_at']
    ordering = ['status', '-created_at']

    def get_serializer_class(self):
        if self.action == 'create_request':
            return ServiceOrderCreateSerializer
        return ServiceOrderSerializer

    def perform_update(self, serializer):
        instance = serializer.save()
        if instance.status == 'completed' and not instance.resolved_at:
            instance.resolved_at = timezone.now()
            instance.save(update_fields=['resolved_at'])

    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        return Response({
            'pending': queryset.filter(status='pending').count(),
            'processing': queryset.filter(status='processing').count(),
            'completed': queryset.filter(status='completed').count(),
            'sos': queryset.filter(request_type='sos').count(),
        })

    @action(detail=False, methods=['get'], url_path='my')
    def my_orders(self, request):
        elder = ensure_elder_profile(request.user)
        if not elder:
            return Response({'detail': '未关联老人档案'}, status=status.HTTP_400_BAD_REQUEST)
        queryset = self.get_queryset().filter(elder=elder)
        return Response(self.get_serializer(queryset, many=True).data)

    @action(detail=False, methods=['post'], url_path='request')
    def create_request(self, request):
        elder = ensure_elder_profile(request.user)
        if not elder:
            return Response({'detail': '未关联老人档案'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        order = ServiceOrder.objects.create(
            elder=elder,
            community=elder.community,
            request_type=data.get('request_type') or 'service',
            service_kind=data.get('service_kind') or 'other',
            title=data.get('title') or '服务请求',
            description=data.get('description') or '',
            preferred_time=data.get('preferred_time') or '',
            contact_phone=data.get('contact_phone') or elder.phone or request.user.phone or '',
            urgency=data.get('urgency') or ('critical' if data.get('request_type') == 'sos' else 'normal'),
        )
        return Response(ServiceOrderSerializer(order).data, status=status.HTTP_201_CREATED)
