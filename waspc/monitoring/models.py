from django.db.models import (DateTimeField,
                              Model,
                              OneToOneField,
                              UUIDField)
from djcelery.models import IntervalSchedule, PeriodicTask
from ..scanner.models import ScanReport
from uuid import uuid4


class Monitor(Model):
    """
    Monitor information
    """
    id = UUIDField(primary_key=True, default=uuid4)
    report = OneToOneField(ScanReport, blank=True, null=True)
    periodic_task = OneToOneField(PeriodicTask)
    modified = DateTimeField(auto_now=True)

    class Meta:
        ordering = ['modified']
        get_latest_by = 'modified'

    def __unicode__(self):
        return self.periodic_task.name
