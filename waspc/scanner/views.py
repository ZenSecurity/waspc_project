from .models import Report
from .serializers import ScannerSerializer
from celery.result import states as celery_states
from config.celery import waspc_celery
from django.http import HttpResponseNotFound
from django.views.generic import TemplateView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.status import (HTTP_200_OK,
                                   HTTP_201_CREATED,
                                   HTTP_202_ACCEPTED,
                                   HTTP_500_INTERNAL_SERVER_ERROR)
from rest_framework.viewsets import ModelViewSet


class ReportTemplateView(TemplateView):
    template_name = 'scanner/report.html'

    def get(self, request, *args, **kwargs):
        report_id = kwargs.get('pk')

        if Report.objects.filter(id=report_id).exists():
            return self.render_to_response(
                context={'report': Report.objects.get(id=report_id)}
            )

        return HttpResponseNotFound('Report: {} not found'.format(report_id))


class ScannerTemplateView(TemplateView):
    template_name = 'scanner/scanner.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response(
            context={
                'scanner_url': reverse(
                    viewname='api:scanner-list',
                    request=request
                )
            }
        )


class ScannerViewSet(ModelViewSet):
    serializer_class = ScannerSerializer
    queryset = Report.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        target_url = serializer.validated_data.get('target_url')

        task_id = waspc_celery.send_task(
            name='Scanner',
            args=[target_url],
            queue='scanner'
        ).id
        task_status = waspc_celery.AsyncResult(task_id).status

        headers = self.get_success_headers(serializer.validated_data)

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

        if Report.objects.filter(id=task_id).exists():
            report = Report.objects.get(id=task_id)
            return Response(
                data={
                    'task_id': report.id,
                    'task_status': celery_states.SUCCESS,
                    'task_result': report.result,
                    'task_finished': report.modified
                },
                status=HTTP_200_OK
            )
        else:
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
                task_report = task_result.get('report', {})

                task_target_url = task_result.get('target_url')

                task.forget()

                scan_report = Report.objects.create(
                    pk=task_id,
                    target_url=task_target_url,
                    result=task_report
                )

                if not len(task_report) or (('exc_type' in task_report) and ('exc_message' in task_report)):
                    return Response(
                        data={
                            'task_id': task_id,
                            'target_url': task_target_url,
                            'task_result': '{exception_type} - {exception_message}'.format(
                                exception_type=getattr(task_report, 'exc_type', None),
                                exception_message=getattr(task_report, 'exc_message', None)
                            ),
                            'task_status': celery_states.FAILURE,
                        },
                        status=HTTP_500_INTERNAL_SERVER_ERROR
                    )
                else:
                    return Response(
                        data={
                            'task_id': task_id,
                            'task_status': task_status,
                            'task_result': task_report,
                            'task_finished': scan_report.modified
                        },
                        status=HTTP_200_OK
                    )
