from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CommunityActivityViewSet,
    FamilyContactViewSet,
    MedicationPlanViewSet,
    ServiceOrderViewSet,
)

router = DefaultRouter()
router.register('service-orders', ServiceOrderViewSet, basename='care-service-orders')
router.register('medications', MedicationPlanViewSet, basename='care-medications')
router.register('activities', CommunityActivityViewSet, basename='care-activities')
router.register('families', FamilyContactViewSet, basename='care-families')

urlpatterns = [
    path('activities/mobile-list/', CommunityActivityViewSet.as_view({'get': 'mobile_list'}), name='care-activities-mobile-list'),
    path('activities/register/', CommunityActivityViewSet.as_view({'post': 'register'}), name='care-activities-register'),
    path('activities/cancel-registration/', CommunityActivityViewSet.as_view({'post': 'cancel_registration'}), name='care-activities-cancel'),
    path('', include(router.urls)),
]
