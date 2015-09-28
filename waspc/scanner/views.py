from .models import ScanReport
from .serializers import ScanReportSerializer, ScannerSerializer
from config.celery import waspc_celery
from django.views.generic import TemplateView
from json import dumps as json_dumps
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.status import (HTTP_200_OK,
                                   HTTP_201_CREATED,
                                   HTTP_202_ACCEPTED,
                                   HTTP_500_INTERNAL_SERVER_ERROR)
from rest_framework.viewsets import ModelViewSet


class ReportTemplateView(TemplateView):
    template_name = 'report.html'

    def get(self, request, *args, **kwargs):
        report_id = kwargs.get('pk')
        context = {}

        if ScanReport.objects.filter(id=report_id).exists():
            report = ScanReport.objects.get(id=report_id)
            context = {
                'target_url': report.target_url,
                'report': json_dumps(report.result),
                'created': report.modified
            }
        return self.render_to_response(context)


class ReportViewSet(ModelViewSet):
    serializer_class = ScanReportSerializer
    queryset = ScanReport.objects.all()


class ScannerTemplateView(TemplateView):
    template_name = 'scanner.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response({
            'scanner_url': reverse(viewname='api:scanner-list', request=request)
        })


class ScannerViewSet(ModelViewSet):
    serializer_class = ScannerSerializer
    queryset = ScanReport.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        target_url = serializer.data.get('target_url')

        task_id = waspc_celery.send_task(
            name='Scanner',
            args=[target_url],
            queue='scanner'
        ).id
        task_status = waspc_celery.AsyncResult(task_id).status

        headers = self.get_success_headers(serializer.data)

        return Response(
            data={
                'task_id': task_id,
                'task_status': task_status,
                'target_url': target_url
            },
            status=HTTP_201_CREATED,
            headers=headers
        )

    def retrieve(self, request, *args, **kwargs):
        task_id = kwargs.get('pk')
        task = waspc_celery.AsyncResult(task_id)
        task_status = task.status

        if task_status in ('STARTED', 'PENDING'):
            return Response(
                data={
                    'task_id': task_id,
                    'task_status': task_status
                },
                status=HTTP_202_ACCEPTED
            )
        else:
            task_result = task.result
            task_report = task_result.get('report')
            task_target_url = task_result.get('target_url')

            task.forget()

            if ('exc_type' in task_report) and ('exc_message' in task_report):
                return Response(
                    data={
                        'task_id': task_id,
                        'target_url': task_target_url,
                        'task_result': '{exception_type} - {exception_message}'.format(
                            exception_type=task_report['exc_type'],
                            exception_message=task_report['exc_message']
                        ),
                        'task_status': 'FAILURE',
                    },
                    status=HTTP_500_INTERNAL_SERVER_ERROR
                )
            else:
                scan_report = ScanReport(
                    target_url=task_target_url,
                    result=task_report
                )
                scan_report.result_url = reverse(
                    viewname='scanner:report',
                    args=[scan_report.pk],
                    request=request
                )
                scan_report.save()

                return Response(
                    data={
                        'task_id': task_id,
                        'task_status': task_status,
                        'task_result': task_report,
                        'task_result_url': scan_report.result_url,
                        'task_finished': scan_report.modified
                    },
                    status=HTTP_200_OK
                )
