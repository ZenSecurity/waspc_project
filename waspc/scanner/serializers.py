from .models import ScanReport
from django.conf import settings
from rest_framework.serializers import (DateTimeField,
                                        ModelSerializer,
                                        ReadOnlyField,
                                        URLField,
                                        UUIDField)


class ScanReportSerializer(ModelSerializer):
    id = UUIDField(read_only=True)
    target_url = URLField(initial=settings.WASPC['scanner']['target_url'])
    result = ReadOnlyField()
    result_url = URLField(read_only=True)
    modified = DateTimeField(read_only=True)

    class Meta:
        model = ScanReport


class ScannerSerializer(ModelSerializer):
    id = UUIDField(read_only=True)
    target_url = URLField(initial=settings.WASPC['scanner']['target_url'])
    result = ReadOnlyField()
    result_url = URLField(read_only=True)
    modified = DateTimeField(read_only=True)

    class Meta:
        model = ScanReport
        fields = ('target_url', 'result_url', 'modified')
