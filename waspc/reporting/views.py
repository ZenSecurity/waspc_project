from .models import Notification, Report
from .serializers import (ReportSerializer,
                          LogstashReportSerializer,
                          NotificationSerializer)
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.views.generic.base import TemplateView
from operator import itemgetter
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from waspc.contrib.jira.connector import APIConnector, JIRAError


def get_reports_difference(new_report, old_report):
    if new_report == old_report:
        return None

    def find_incident(sequence, item):
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

    def dict_to_tuple(dictionary):
        result_tuple = ()
        for key, value in dictionary.iteritems():
            if isinstance(value, dict):
                value = dict_to_tuple(value)
            result_tuple += ((key, value),)
        return result_tuple

    def tuple_to_dict(input_tuple):
        result_dict = {}
        for key, value in input_tuple:
            if isinstance(value, tuple):
                value = tuple_to_dict(value)
            result_dict[key] = value
        return result_dict

    old_report_data = old_report['data']
    old_report_metadata = old_report['metadata']
    new_report_data = new_report['data']
    new_report_metadata = new_report['metadata']

    result_report = {
        'data': {},
        'metadata': {}
    }
    result_report_data = result_report['data']
    result_report_metadata = result_report['metadata']

    for category in new_report_data:
        if category in old_report_data:
            result_report_data[category] = {}
            for severity in new_report_data[category]:
                result_report_data[category][severity] = {}
                pair_incidents_indexes = []
                if severity in old_report_data[category]:
                    old_report_data[category][severity] = set(
                        dict_to_tuple(incident) for incident in old_report_data[category][severity]
                    )
                    old_report_data[category][severity] = sorted(
                        [tuple_to_dict(incident) for incident in old_report_data[category][severity]],
                        key=itemgetter('data')
                    )
                    new_report_data[category][severity] = set(
                        dict_to_tuple(incident) for incident in new_report_data[category][severity]
                    )
                    new_report_data[category][severity] = sorted(
                        [tuple_to_dict(incident) for incident in new_report_data[category][severity]],
                        key=itemgetter('data')
                    )
                    result_report_data[category][severity] = []
                    for new_report_incident in new_report_data[category][severity]:
                        new_report_incident_index = find_incident(old_report_data[category][severity], new_report_incident)
                        if new_report_incident_index is not None:
                            old_report_incident = old_report_data[category][severity][new_report_incident_index]
                            if new_report_incident == old_report_incident:
                                result_report_data[category][severity].append(new_report_incident)
                            else:
                                incident = {
                                    'data': new_report_incident['data'],
                                    'metadata': {}
                                }
                                incident['metadata'].update(old_report_incident.get('metadata', {}))
                                incident['metadata'].update(new_report_incident.get('metadata', {}))

                                result_report_data[category][severity].append(incident)
                            pair_incidents_indexes.append(new_report_incident_index)
                        else:
                            result_report_data[category][severity].append(new_report_incident)

                    unique_old_report_incidents_indexes = set(xrange(len(old_report_data[category][severity]))) - set(pair_incidents_indexes)
                    result_report_data[category][severity] += [
                        old_report_data[category][severity][unique_old_report_incident_index] for unique_old_report_incident_index in unique_old_report_incidents_indexes
                    ]
                else:
                    result_report_data[category][severity] = new_report_data[category][severity]

            for severity in set(old_report_data[category]).difference(new_report_data[category]):
                result_report_data[category][severity] = old_report_data[category][severity]
        else:
            result_report_data[category] = new_report_data[category]

    for category in set(old_report_data).difference(new_report_data):
        result_report_data[category] = old_report_data[category]
        result_report_metadata[category] = old_report_metadata[category]

    result_report_metadata.update(new_report_metadata)

    return None if result_report == old_report else result_report


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
            severity_value = severities_values[severity]
            for incident in report_data[category][severity]:
                incident_status = incident.get('metadata', {}).get('reporting_status', 'pending')
                if incident_status == 'pending' and severity_value > report_severity_value:
                    report_severity_value = severity_value

    return report_severity_value


def update_jira_issues(report):
    report_data = report.get('data')
    report_metadata = report.get('metadata')
    jira_issue_description = report_metadata.get('jira_issue_description')
    new_issue_permalink = ''
    new_issue_status = ''

    if jira_issue_description:

        def get_new_issue_priority(report):
            issues_priority = settings.WASPC['reporting']['jira']['issues_priority']

            severities_values = {
                'information': 1,
                'low': 2,
                'medium': 3,
                'high': 4
            }

            issue_priority = severities_values['information']

            for category in report_data:
                for severity in report_data[category]:
                    for incident in report_data[category][severity]:
                        incident_status = incident.get('metadata', {}).get('reporting_status', 'pending')
                        incident_url = incident.get('metadata', {}).get('issue_url')
                        if incident_status == 'done' and not incident_url and severities_values[severity] > issue_priority:
                            issue_priority = severities_values[severity]

            severities_values = {
                1: 'information',
                2: 'low',
                3: 'medium',
                4: 'high'
            }

            return issues_priority[severities_values[issue_priority]]

        connection = APIConnector()
        new_issue = connection.create_issue(
            project={'key': settings.WASPC['reporting']['jira']['project']},
            summary='{module} {target_url}'.format(
                module=report_metadata.get('module'),
                target_url=report_metadata.get('target_url')
            ),
            description=jira_issue_description,
            issuetype={'name': settings.WASPC['reporting']['jira']['issue_type']},
            priority={'name': get_new_issue_priority(report)}
        )

        new_issue_permalink = new_issue.permalink()
        new_issue_status = new_issue.fields.status.name

        del report_metadata['jira_issue_description']

    for category in report_data:
        for severity in report_data[category]:
            for incident in report_data[category][severity]:
                incident_metadata = incident.get('metadata', {})
                incident_reporting_status = incident_metadata.get('reporting_status')
                incident_issue_status = incident_metadata.get('issue_status', '')

                if incident_reporting_status == 'done' and not incident_issue_status:
                    incident_metadata['issue_url'] = new_issue_permalink
                    incident_metadata['issue_status'] = new_issue_status
                else:
                    issues_url = incident_metadata.get('issue_url')
                    if issues_url:
                        issue_name = issues_url.split('/')[-1]
                        try:
                            connection = APIConnector()
                            incident_metadata['issue_status'] = connection.issue(issue_name).fields.status.name
                        except JIRAError as exception:
                            print "{type} {message}".format(
                                type=exception.__class__.__name__,
                                message=unicode(exception)
                            )
    return report


class ProcessReportTemplateView(TemplateView):
    template_name = 'reporting/process.html'

    def get(self, request, *args, **kwargs):
        report_id = kwargs.get('pk')

        if Report.objects.filter(id=report_id).exists():
            current_report = Report.objects.get(id=report_id)
            reports = Report.objects.filter(broker=current_report.broker)
            if reports.exists():
                latest_report = reports.latest()
                if current_report != latest_report:
                    return HttpResponseRedirect(
                        reverse(viewname='reporting:process', args=[latest_report.pk])
                    )

            current_report.report = update_jira_issues(current_report.report)

            return self.render_to_response(
                context={
                    'report': current_report,
                    'report_url': reverse(
                        viewname='api:reporting-detail',
                        args=[report_id],
                        request=request
                    )
                }
            )

        return HttpResponseNotFound('Report: {} not found'.format(report_id))


class ReportTemplateView(TemplateView):
    template_name = 'reporting/report.html'

    def get(self, request, *args, **kwargs):
        report_id = kwargs.get('pk')
        current_report = Report.objects.get(id=report_id)

        return self.render_to_response(context={'report': current_report})


class ReportViewSet(ModelViewSet):
    serializer_class = ReportSerializer
    queryset = Report.objects.order_by('broker', '-modified').distinct('broker')

    def create(self, request, *args, **kwargs):
        serializer = LogstashReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        messages = serializer.validated_data.get('message')

        for message in messages:
            old_broker_reports = self.queryset.filter(broker=message.get('broker'))
            if old_broker_reports.exists():
                message_request = Request(request)
                message_request._full_data = message
                self.kwargs['pk'] = old_broker_reports.first().pk
                self.update(message_request)
            else:
                new_broker_report = Report.objects.create(
                    broker=message.get('broker'),
                    report=message.get('report')
                )

                Notification.objects.create(
                    severity=get_report_severity(message.get('report')),
                    report=new_broker_report
                )

        return Response(status=HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        new_report = serializer.validated_data.get('report')
        broker = serializer.validated_data.get('broker')

        broker_reports = self.queryset.filter(broker=broker)
        broker_report_object = broker_reports.first()
        broker_report = broker_report_object.report

        reports_difference = get_reports_difference(new_report, broker_report)

        if not reports_difference:
            return Response(status=HTTP_204_NO_CONTENT)

        reports_difference = update_jira_issues(reports_difference)

        broker_notifications = Notification.objects.filter(report=broker_report_object)

        broker_notification = broker_notifications.first()
        broker_notification.severity = get_report_severity(reports_difference)
        broker_notification.report = Report.objects.create(
            broker=broker,
            report=reports_difference
        )
        broker_notification.save()

        return Response(status=HTTP_200_OK)


class NotificationViewSet(ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        serializer_data = serializer.data
        # TODO: need to fix that shit
        for data in serializer_data:
            report = data.get('report', {})
            data.update(report)
            data.update(report.get('report', {}).get('metadata', {}))
            data.update(
                {
                    'report_url': reverse(
                        viewname='reporting:process',
                        args=[report.get('id')],
                        request=request
                    )
                }
            )
            del data['report']

        return Response(serializer.data)
