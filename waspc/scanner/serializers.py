from .models import ScanReport
from django.conf import settings
from rest_framework.serializers import (ModelSerializer,
                                        ReadOnlyField,
                                        URLField,
                                        UUIDField)


class ScanReportSerializer(ModelSerializer):
    id = UUIDField(read_only=True)
    result_url = URLField(read_only=True)
    result = ReadOnlyField()
    target_url = URLField(initial=settings.WASPC['scanner']['target_url'])

    class Meta:
        model = ScanReport


class ScannerSerializer(ModelSerializer):
    target_url = URLField(initial=settings.WASPC['scanner']['target_url'])
    result_url = URLField(read_only=True)

    class Meta:
        model = ScanReport
        fields = ('target_url', 'result_url', 'modified')
