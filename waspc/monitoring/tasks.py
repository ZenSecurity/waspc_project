from .models import (Monitor,
                     PeriodicTask,
                     Report)
from ..scanner.tasks import Scanner
from celery import Task
from config.celery import waspc_celery


class PeriodicScanner(Scanner):

    name = 'PeriodicScanner'

    def run(self, target_url):
        self._target_url = target_url
        self.scan()

        periodic_task = PeriodicTask.objects.get(
            name=target_url
        )

        monitor = Monitor.objects.get(
            periodic_task=periodic_task
        )

        monitor.report = Report(
            result=self.get_report()
        )
        monitor_report = monitor.report
        monitor_report.target_url = target_url
        monitor_report.save()

        monitor.save()


class Monitoring(Task):

    name = 'Monitoring'

    def run(self, target_url, expires):
        waspc_celery.send_task(
            name='PeriodicScanner',
            args=[target_url],
            queue='scanner',
            expires=expires
        )
