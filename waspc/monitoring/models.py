from django.db.models import (DateTimeField,
                              Model,
                              OneToOneField,
                              QuerySet,
                              UUIDField)
from djcelery.models import IntervalSchedule, PeriodicTask
from ..scanner.models import Report
from uuid import uuid4


class MonitorQuerySet(QuerySet):
    def delete(self, *args, **kwargs):
        for monitor in self:
            monitor.periodic_task.delete()
            monitor.delete()
        super(MonitorQuerySet, self).delete(*args, **kwargs)


class Monitor(Model):
    """
    Monitor information
    """
    objects = MonitorQuerySet.as_manager()

    id = UUIDField(primary_key=True, default=uuid4)
    report = OneToOneField(Report, blank=True, null=True)
    periodic_task = OneToOneField(PeriodicTask)
    modified = DateTimeField(auto_now=True)

    class Meta:
        ordering = ['modified']
        get_latest_by = 'modified'

    def __unicode__(self):
        return self.periodic_task.name
