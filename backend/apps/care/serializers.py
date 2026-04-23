from rest_framework import serializers
from django.utils import timezone

from .models import (
    ActivityRegistration,
    CommunityActivity,
    FamilyContact,
    MedicationPlan,
    ServiceOrder,
)


class FamilyContactSerializer(serializers.ModelSerializer):
    elder_name = serializers.CharField(source='elder.name', read_only=True)
    community_name = serializers.CharField(source='elder.community.name', read_only=True)
    relation_display = serializers.CharField(source='get_relation_display', read_only=True)

    class Meta:
        model = FamilyContact
        fields = '__all__'


class MedicationPlanSerializer(serializers.ModelSerializer):
    elder_name = serializers.CharField(source='elder.name', read_only=True)
    community_name = serializers.CharField(source='elder.community.name', read_only=True)
    taken_today = serializers.SerializerMethodField()

    class Meta:
        model = MedicationPlan
        fields = '__all__'

    def get_taken_today(self, obj):
        if not obj.last_taken_at:
            return False
        local_time = timezone.localtime(obj.last_taken_at)
        return local_time.date() == timezone.localdate()


class CommunityActivitySerializer(serializers.ModelSerializer):
    registration_count = serializers.SerializerMethodField()
    is_registered = serializers.SerializerMethodField()
    registration_id = serializers.SerializerMethodField()
    spots_left = serializers.SerializerMethodField()

    class Meta:
        model = CommunityActivity
        fields = '__all__'

    def get_registration_count(self, obj):
        return obj.registrations.filter(status='registered').count()

    def get_is_registered(self, obj):
        elder = self.context.get('elder')
        if not elder:
            return False
        return obj.registrations.filter(elder=elder, status='registered').exists()

    def get_registration_id(self, obj):
        elder = self.context.get('elder')
        if not elder:
            return None
        registration = obj.registrations.filter(elder=elder).first()
        return registration.id if registration else None

    def get_spots_left(self, obj):
        max_count = obj.max_participants or 0
        if max_count <= 0:
            return 0
        left = max_count - obj.registrations.filter(status='registered').count()
        return left if left > 0 else 0


class ActivityRegistrationSerializer(serializers.ModelSerializer):
    elder_name = serializers.CharField(source='elder.name', read_only=True)
    activity_title = serializers.CharField(source='activity.title', read_only=True)

    class Meta:
        model = ActivityRegistration
        fields = '__all__'


class ServiceOrderSerializer(serializers.ModelSerializer):
    elder_name = serializers.CharField(source='elder.name', read_only=True)
    community_name = serializers.CharField(source='community.name', read_only=True)
    request_type_display = serializers.CharField(source='get_request_type_display', read_only=True)
    service_kind_display = serializers.CharField(source='get_service_kind_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    urgency_display = serializers.CharField(source='get_urgency_display', read_only=True)

    class Meta:
        model = ServiceOrder
        fields = '__all__'


class ServiceOrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceOrder
        fields = [
            'request_type', 'service_kind', 'title', 'description',
            'preferred_time', 'contact_phone', 'urgency',
        ]
