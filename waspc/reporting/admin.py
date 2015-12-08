from .models import Notification, Report
from django.core.urlresolvers import reverse
from django.contrib import admin
from django.utils.html import format_html


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    def id(instance):
        report_pk = instance.report.pk
        return format_html(
            '<a href="{0}" target="_blank">{1}</a>',
            reverse(viewname='reporting:process', args=[report_pk]),
            instance.pk
        )

    def module(self, instance):
        return instance.report.report.get('metadata', {}).get('module')

    def target(self, instance):
        return instance.report.report.get('metadata', {}).get('target_url')

    def categories(self, instance):
        categories = []
        report_data = instance.report.report.get('data')
        for category in report_data:
            for severity in report_data[category]:
                for incident in report_data[category][severity]:
                    incident_status = incident.get('metadata', {}).get('reporting_status', 'pending')
                    if incident_status == 'pending' and category not in categories:
                        categories.append(category)

        return ', '.join(sorted(categories))

    list_display = (id, 'target', 'module', 'categories', 'severity', 'modified')
    search_fields = ('id',)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    def id(instance):
        instance_pk = instance.pk
        return format_html(
            '<a href="{0}" target="_blank">{1}</a>',
            reverse(viewname='reporting:report', args=[instance_pk]),
            instance_pk
        )

    list_display = (id, 'broker', 'modified')
    search_fields = ('broker',)
