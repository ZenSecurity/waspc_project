from django.db.models import (DateTimeField,
                              Model,
                              URLField,
                              UUIDField)
from jsonfield import JSONField
from uuid import uuid4


class Report(Model):
    """
    Stores scan report
    """
    id = UUIDField(primary_key=True, default=uuid4)
    target_url = URLField()
    result = JSONField(blank=True)
    modified = DateTimeField(auto_now=True)

    class Meta:
        ordering = ['modified']
        get_latest_by = 'modified'

    def __unicode__(self):
        return '{target_url} {execution_finished}'.format(
            target_url=self.target_url,
            execution_finished=self.modified
        )
