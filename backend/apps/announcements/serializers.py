from rest_framework import serializers
from .models import Announcement


class AnnouncementSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    audience_display = serializers.CharField(source='get_audience_display', read_only=True)
    cover_url = serializers.SerializerMethodField()

    class Meta:
        model = Announcement
        fields = [
            'id', 'title', 'summary', 'content', 'category', 'category_display',
            'audience', 'audience_display', 'cover_image', 'cover_url',
            'is_pinned', 'is_active', 'publish_at', 'created_at', 'updated_at',
        ]

    def get_cover_url(self, obj):
        if not obj.cover_image:
            return ''
        request = self.context.get('request')
        url = obj.cover_image.url
        return request.build_absolute_uri(url) if request else url
