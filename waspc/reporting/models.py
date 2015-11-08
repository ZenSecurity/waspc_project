from django.db.models import (DateTimeField,
                              CharField,
                              IntegerField,
                              Model,
                              OneToOneField,
                              UUIDField)
from jsonfield import JSONField
from uuid import uuid4


class Report(Model):
    """
    Report information
    """
    id = UUIDField(primary_key=True, default=uuid4)
    broker = CharField(max_length=128)
    report = JSONField(
        default={
            'data': {},
            'metadata': {}
        }
    )
    modified = DateTimeField(auto_now=True)

    class Meta:
        ordering = ['broker', 'modified']
        get_latest_by = 'modified'

    def __unicode__(self):
        return '{broker} {execution_finished}'.format(
            broker=self.broker,
            execution_finished=self.modified
        )


class Notification(Model):
    SEVERITY_VALUES = (
        (0, 'ok'),
        (1, 'information'),
        (2, 'low'),
        (3, 'medium'),
        (4, 'high')
    )
    id = UUIDField(primary_key=True, default=uuid4)
    severity = IntegerField(choices=SEVERITY_VALUES)
    report = OneToOneField(Report)
    modified = DateTimeField(auto_now=True)

    class Meta:
        ordering = ['modified']
        get_latest_by = 'modified'

    def __unicode__(self):
        return '{id} {severity}'.format(
            id=self.id,
            severity=self.SEVERITY_VALUES[self.severity][1]
        )
