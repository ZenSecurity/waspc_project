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
    fields = ('id', 'severity', 'modified')
    list_display = (id, 'severity', 'modified')
    search_fields = ('id',)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    def id(instance):
        instance_pk = instance.pk
        return format_html(
            '<a href="{0}" target="_blank">{1}</a>',
            reverse(viewname='reporting:history', args=[instance_pk]),
            instance_pk
        )

    fields = ('id', 'broker', 'modified')
    list_display = (id, 'broker', 'modified')
    search_fields = ('broker',)
