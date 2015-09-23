from .models import ScanReport
from rest_framework.serializers import ModelSerializer


class ScanReportSerializer(ModelSerializer):

    class Meta:
        model = ScanReport


class ScannerSerializer(ModelSerializer):

    class Meta:
        model = ScanReport
        fields = ('target_url', 'result_url', 'modified')
