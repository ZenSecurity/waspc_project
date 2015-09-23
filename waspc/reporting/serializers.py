from .models import Notification, Report
from rest_framework.serializers import (ModelSerializer,
                                        Serializer,
                                        ValidationError)


class ReportSerializer(ModelSerializer):

    class Meta:
        model = Report
        fields = ('id', 'broker', 'report', 'report_url')

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
    report = ReportSerializer()

    class Meta:
        model = Notification
        fields = ('id', 'severity', 'report', 'modified')
