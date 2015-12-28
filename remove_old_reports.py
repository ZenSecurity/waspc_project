#!/usr/bin/env python

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.common")

import django
django.setup()

from waspc.reporting.models import Report, Notification


notifications = Notification.objects.all()
notifications_reports_ids = [notification.report.id for notification in notifications]

start_index = 0
reports_counter = Report.objects.count()
reports_limit = 10000


for end_index in xrange(reports_limit, reports_counter, reports_limit):
  for report in Report.objects.all()[start_index:end_index]:
    if report.id not in notifications_reports_ids:
      report.delete()
  start_index = end_index

for report in Report.objects.all()[start_index:]:
  if report.id not in notifications_reports_ids:
    report.delete()
