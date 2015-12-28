#!/usr/bin/env python

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.common")

import django
django.setup()


from json import loads as json_loads, dumps as json_dumps
from waspc.reporting.models import Report, Notification
from pprint import pprint

targets = json_loads(open('urls_result.txt').read())
targets = [target for target in targets if ('status' in targets[target]) and targets[target]['status'] != 200]

for notification in Notification.objects.all():
    print notification.report.id
    if notification.report.report['metadata']['target_url'] in targets:
        for category in  notification.report.report['data']:
            for severity in notification.report.report['data'][category]:
                severity_incidents = notification.report.report['data'][category][severity]
                for incident in severity_incidents:
                    if 'metadata' not in incident:
                        incident['metadata'] = {}
                    incident['metadata']['reporting_status'] = "false"
                #pprint(severity_incidents)
                #raw_input()
    notification.report.save()
print 'done'
