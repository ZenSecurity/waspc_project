from .models import (IntervalSchedule,
                     Monitor,
                     PeriodicTask)
from ..scanner.serializers import ScanReportSerializer
from django.conf import settings
from json import dumps as json_dumps, loads as json_loads
from rest_framework.serializers import (CharField,
                                        IntegerField,
                                        ModelSerializer,
                                        UUIDField)


class IntervalScheduleSerializer(ModelSerializer):
    every = IntegerField(
        initial=settings.WASPC['monitoring']['every'],
    )
    period = CharField(
        initial=settings.WASPC['monitoring']['period'],
    )

    class Meta:
        model = IntervalSchedule
        fields = ('every', 'period')


class PeriodicTaskSerializer(ModelSerializer):
    interval = IntervalScheduleSerializer()

    class Meta:
        model = PeriodicTask
        fields = ('interval',)


class MonitorSerializer(ModelSerializer):
    id = UUIDField(read_only=True)
    periodic_task = PeriodicTaskSerializer()
    report = ScanReportSerializer(required=False)

    class Meta:
        model = Monitor

    def create(self, validated_data):
        target_url = validated_data.get('report').get('target_url')
        scan_interval = validated_data.get('periodic_task', {}).get('interval', {})

        interval_schedule, interval_schedule_created = IntervalSchedule.objects.get_or_create(
            every=scan_interval.get('every', settings.WASPC['monitoring']['every']),
            period=scan_interval.get('period', settings.WASPC['monitoring']['period'])
        )

        periodic_task = PeriodicTask.objects.create(
            name=target_url,
            task='Monitoring',
            kwargs=json_dumps({
                'target_url': target_url,
                'expires': interval_schedule.schedule.run_every.seconds
            }),
            interval=interval_schedule,
            queue='monitoring'
        )

        monitor = Monitor.objects.create(
            periodic_task=periodic_task
        )

        return monitor

    def update(self, monitor, validated_data):
        scan_interval = validated_data.get('periodic_task', {}).get("interval", {})

        if scan_interval:
            interval_schedule, interval_schedule_created = IntervalSchedule.objects.get_or_create(
                every=scan_interval.get('every', settings.WASPC['monitoring']['every']),
                period=scan_interval.get('period', settings.WASPC['monitoring']['period'])
            )

            monitor_periodic_task = monitor.periodic_task
            monitor_periodic_task_old_interval = monitor_periodic_task.interval
            monitor_periodic_task.interval = interval_schedule

            kwargs = json_loads(monitor_periodic_task.kwargs)
            kwargs['expires'] = interval_schedule.schedule.run_every.seconds
            monitor_periodic_task.kwargs = json_dumps(kwargs)

            if not PeriodicTask.objects.exclude(
                    pk=monitor_periodic_task.pk
            ).filter(
                interval=monitor_periodic_task_old_interval
            ).exists():
                monitor_periodic_task_old_interval.delete()

            monitor_periodic_task.save()
            monitor.save()

        return monitor
