from .models import Notification, Report
from rest_framework.serializers import (CharField,
                                        DateTimeField,
                                        IntegerField,
                                        ModelField,
                                        ModelSerializer,
                                        Serializer,
                                        ValidationError,
                                        URLField,
                                        UUIDField)


class ReportSerializer(ModelSerializer):
    id = UUIDField(read_only=True)
    broker = CharField(initial="")
    report = ModelField(
        model_field=Report()._meta.get_field('report'),
        initial={
            'data': {},
            'metadata': {}
        }
    )
    report_url = URLField(read_only=True)
    modified = DateTimeField(read_only=True)

    class Meta:
        model = Report

    def validate_report(self, report):
        if 'data' not in report or 'metadata' not in report:
            raise ValidationError('Report has wrong format.')

        severities = ('information', 'low', 'medium', 'high')

        report_data = report['data']
        for category in report_data:
            for severity in report_data[category]:
                if severity not in severities:
                    raise ValidationError('Report format has validation error.')
                for incident in report_data[category][severity]:
                    if 'data' not in incident:
                        raise ValidationError('Report format has validation error.')
        return report


class LogstashReportSerializer(Serializer):
    message = ReportSerializer(many=True)


class NotificationSerializer(ModelSerializer):
    id = UUIDField(read_only=True)
    severity = IntegerField(initial=0)
    report = ReportSerializer(read_only=True)
    modified = DateTimeField(read_only=True)

    class Meta:
        model = Notification
