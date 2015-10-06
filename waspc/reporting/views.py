from .models import Notification, Report
from .serializers import (ReportSerializer,
                          LogstashReportSerializer,
                          NotificationSerializer)
from django.views.generic import TemplateView
from json import dumps as json_dumps
from operator import itemgetter
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_201_CREATED
from rest_framework.viewsets import ModelViewSet


class NotificationViewSet(ModelViewSet):
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        serializer_data = serializer.data

        # todo: need to fix that shit
        for data in serializer_data:
            data_report = data['report']
            report = data_report['report']
            if 'metadata' in report:
                report_metadata = report['metadata']
                notification_metadata = set(report_metadata) - set(report['data'])
                for metadata in notification_metadata:
                    data[metadata] = report_metadata[metadata]
            if 'report_url' in data_report:
                data['report_url'] = data_report['report_url']
            del data['report']

        return Response(serializer.data)


def get_reports_difference(new_report, old_report):

    new_report_data = new_report['data']
    old_report_data = old_report['data']

    if not new_report_data or not old_report_data:
        return new_report

    result_report = {
        'data': {},
        'metadata': {}
    }

    if new_report_data == old_report_data:
        return result_report

    def incident_binary_search(sequence, item):
        low, high = 0, len(sequence)
        while low < high:
            middle = (low + high) // 2
            sequence_middle = sequence[middle]
            if item['data'] > sequence_middle['data']:
                low = middle + 1
            elif item['data'] < sequence_middle['data']:
                high = middle
            else:
                return middle
        return None

    new_report_metadata = new_report['metadata']
    old_report_metadata = old_report['metadata']

    result_report_data = result_report['data']
    result_report_metadata = result_report['metadata']

    for category in new_report_data:
        if category in old_report_data:
            result_report_data[category] = {}
            for severity in new_report_data[category]:
                result_report_data[category][severity] = {}
                if severity in old_report_data[category]:
                    old_report_data[category][severity].sort(key=itemgetter('data'))
                    result_report_data[category][severity] = []
                    new_report_data[category][severity].sort(key=itemgetter('data'))
                    for incident_dataset in new_report_data[category][severity]:
                        incident_index = incident_binary_search(old_report_data[category][severity], incident_dataset)
                        if incident_index is not None:
                            old_report_data_incident_dataset = old_report_data[category][severity][incident_index]
                            if incident_dataset == old_report_data_incident_dataset:
                                result_report_data[category][severity].append(incident_dataset)
                            else:
                                new_incident_dataset = {
                                    'data': incident_dataset['data'],
                                    'metadata': {}
                                }
                                if 'metadata' in old_report_data_incident_dataset:
                                    for metadata in old_report_data_incident_dataset['metadata']:
                                        new_incident_dataset['metadata'][metadata] = old_report_data_incident_dataset['metadata'][metadata]
                                if 'metadata' in incident_dataset:
                                    for metadata in incident_dataset['metadata']:
                                        new_incident_dataset['metadata'][metadata] = incident_dataset['metadata'][metadata]
                                result_report_data[category][severity].append(new_incident_dataset)
                        else:
                            result_report_data[category][severity].append(incident_dataset)
                else:
                    result_report_data[category][severity] = new_report_data[category][severity]
            if category in old_report_metadata:
                result_report_metadata[category] = old_report_metadata[category]
        else:
            result_report_data[category] = new_report_data[category]
            if category in new_report_metadata:
                result_report_metadata[category] = new_report_metadata[category]

    if old_report_data == new_report_data:
        return {
            'data': {},
            'metadata': {}
        }

    if result_report_data:
        report_metadata = set(new_report_metadata) - set(new_report_data)
        for metadata in report_metadata:
            result_report_metadata[metadata] = new_report_metadata[metadata]

    return result_report


def get_report_severity(report):
    severities_values = {
        'ok': 0,
        'information': 1,
        'low': 2,
        'medium': 3,
        'high': 4
    }

    report_severity_value = severities_values['ok']
    report_data = report['data']
    for category in report_data:
        for severity in report_data[category]:
            severity_status = 'closed'
            for incident_dataset in report_data[category][severity]:
                incident_dataset_status = incident_dataset.get('metadata', {}).get('status', 'open')
                severity_status = 'open' if incident_dataset_status == 'open' else severity_status
            if severity_status == 'open':
                severity_value = severities_values[severity]
                if severity_value > report_severity_value:
                    report_severity_value = severity_value
    return report_severity_value


class ReportTemplateView(TemplateView):
    template_name = 'reporting.html'

    def get(self, request, *args, **kwargs):
        report_id = kwargs.get('pk')
        context = {}

        if Report.objects.filter(id=report_id).exists():
            report = Report.objects.get(id=report_id)
            broker_reports = Report.objects.filter(
                broker=report.broker
            )
            current_report_url = None
            if broker_reports.exists():
                report_url = broker_reports.latest().report_url
                current_report_url = report_url if report_url != report.report_url else None

            context = {
                'report': json_dumps(report.report),
                'report_created': report.modified,
                'target_url': report.report['metadata']['target_url'],
                'report_module': report.report['metadata']['module'],
                'report_broker': report.broker,
                'current_report_url': current_report_url,
                'reporting_url': reverse(
                    viewname='api:reporting-list',
                    request=request
                )
            }
        return self.render_to_response(context)


class ReportViewSet(ModelViewSet):
    serializer_class = ReportSerializer
    queryset = Report.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = LogstashReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message = serializer.data.get('message')

        for report in message:
            broker = report['broker']
            new_report = report['report']

            old_broker_reports = Report.objects.filter(
                broker=broker
            )

            old_broker_report, old_report = None, None
            if old_broker_reports.exists():
                old_broker_report = old_broker_reports.latest()
                old_report = old_broker_report.report
            else:
                old_report = {
                    'data': {},
                    'metadata': {}
                }

            result_report = get_reports_difference(new_report, old_report)
            result_report_severity = get_report_severity(result_report)

            broker_notifications = Notification.objects.filter(
                report=old_broker_report
            )

            broker_notification_report = Report(
                broker=broker,
                report=result_report
            )
            broker_notification_report.report_url = reverse(
                viewname='reporting:report',
                args=[broker_notification_report.pk],
                request=request
            )

            if broker_notifications.exists():
                broker_notification = broker_notifications.latest()
                if broker_notification.report.report != result_report:
                    broker_notification_report.save()
                    broker_notification.severity = result_report_severity
                    broker_notification.report = broker_notification_report
                    broker_notification.save()
            # else:
            #     broker_notification_report.save()
            #     Notification.objects.create(
            #         severity=result_report_severity,
            #         report=broker_notification_report
            #     )

        return Response(
            data=message,
            status=HTTP_201_CREATED,
        )
