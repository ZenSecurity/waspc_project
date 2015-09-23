from .models import Monitor, PeriodicTask
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.status import HTTP_204_NO_CONTENT
from serializers import MonitorSerializer


class MonitorViewSet(ModelViewSet):

    serializer_class = MonitorSerializer
    queryset = Monitor.objects.all()

    def destroy(self, request, *args, **kwargs):
        monitor = self.get_object()
        monitor_periodic_task = monitor.periodic_task

        if not PeriodicTask.objects.exclude(
            pk=monitor_periodic_task.pk
        ).filter(
            interval=monitor_periodic_task.interval
        ).exists():
            monitor_periodic_task.interval.delete()

        monitor_periodic_task.delete()
        self.perform_destroy(monitor)

        return Response(status=HTTP_204_NO_CONTENT)
