from .models import Notification, Report
from .serializers import (ReportSerializer,
                          LogstashReportSerializer,
                          NotificationSerializer)
from django.views.generic import TemplateView
from operator import itemgetter
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet


class NotificationViewSet(ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        serializer_data = serializer.data

        # TODO: need to fix that shit
        for data in serializer_data:
            data_report = data['report']
            report = data_report['report']
            if 'metadata' in report:
                report_metadata = report['metadata']
                notification_metadata = set(report_metadata) - set(report['data'])
                for metadata in notification_metadata:
                    data[metadata] = report_metadata[metadata]
            if 'report_url' in data_report:
                data['report_url'] = reverse(
                    viewname='reporting:process',
                    args=[data_report['id']],
                    request=request
                )
            if 'broker' in data_report:
                data['broker'] = data_report['broker']

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
        return None

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
        return None

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


class HistoryReportTemplateView(TemplateView):
    template_name = 'history.html'

    def get(self, request, *args, **kwargs):
        report_id = kwargs.get('pk')
        context = {}

        if Report.objects.filter(id=report_id).exists():
            report = Report.objects.get(id=report_id)
            context = {
                'report': report
            }
        return self.render_to_response(context)


class ProcessReportTemplateView(TemplateView):
    template_name = 'process.html'

    def get(self, request, *args, **kwargs):
        report_id = kwargs.get('pk')
        context = {}

        if Report.objects.filter(id=report_id).exists():
            report = Report.objects.get(id=report_id)
            broker_reports = Report.objects.filter(broker=report.broker)
            latest_report_url = None
            if broker_reports.exists():
                latest_broker_report = broker_reports.latest()
                if report != latest_broker_report:
                    latest_report_url = reverse(
                        viewname='reporting:process',
                        args=[latest_broker_report.pk],
                        request=request
                    )

            context = {
                'report': report,
                'latest_report_url': latest_report_url,
                'report_url': reverse(
                    viewname='api:reporting-detail',
                    args=[report_id],
                    request=request
                )
            }

        return self.render_to_response(context)


class ReportViewSet(ModelViewSet):
    serializer_class = ReportSerializer
    queryset = Report.objects.order_by('broker', '-modified').distinct('broker')

    def create(self, request, *args, **kwargs):
        serializer = LogstashReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        messages = serializer.validated_data.get('message')

        for message in messages:
            old_broker_reports = self.queryset.filter(broker=message['broker'])
            if old_broker_reports.exists():
                message_request = Request(request)
                message_request._full_data = message
                self.kwargs[u'pk'] = old_broker_reports.first().pk

                return self.update(message_request)

            new_broker_report = Report(
                broker=message['broker'],
                report=message['report']
            )
            new_broker_report.report_url = reverse(
                viewname='reporting:process',
                args=[new_broker_report.pk],
                request=request
            )
            new_broker_report.save()

            Notification.objects.create(
                severity=get_report_severity(message['report']),
                report=new_broker_report
            )

        return Response(
            data=messages,
            status=HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        new_report = serializer.validated_data['report']
        broker = serializer.validated_data['broker']

        broker_reports = self.queryset.filter(broker=broker)
        broker_report_object = broker_reports.first()
        broker_report = broker_report_object.report

        reports_difference = get_reports_difference(new_report, broker_report)
        if not reports_difference:
            return Response(status=HTTP_204_NO_CONTENT)

        broker_notifications = Notification.objects.filter(report=broker_report_object)
        broker_notification = broker_notifications.first()

        new_broker_report_object = Report(
            broker=broker,
            report=reports_difference
        )
        new_broker_report_object.report_url = reverse(
            viewname='reporting:process',
            args=[new_broker_report_object.pk],
            request=request
        )
        new_broker_report_object.save()

        broker_notification.severity = get_report_severity(reports_difference)
        broker_notification.report = new_broker_report_object
        broker_notification.save()

        return Response(
            data=serializer.data,
            status=HTTP_201_CREATED
        )
