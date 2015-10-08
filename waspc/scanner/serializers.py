from .models import ScanReport
from django.conf import settings
from rest_framework.serializers import (DateTimeField,
                                        ModelField,
                                        ModelSerializer,
                                        URLField,
                                        UUIDField)


class ScannerSerializer(ModelSerializer):
    id = UUIDField(read_only=True)
    target_url = URLField(initial=settings.WASPC['scanner']['target_url'])
    result = ModelField(model_field=ScanReport()._meta.get_field('result'), read_only=True)
    result_url = URLField(read_only=True)
    modified = DateTimeField(read_only=True)

    class Meta:
        model = ScanReport
