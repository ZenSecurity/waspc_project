from .models import Notification, Report
from django.contrib import admin
from django.utils.html import format_html


class NotificationAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'report')


class ReportAdmin(admin.ModelAdmin):
    fields = ('id', 'broker', 'report', 'report_url_link')
    readonly_fields = ('id', 'report_url_link', 'broker')
    search_fields = ('id',)

    def report_url_link(self, instance):
        return format_html('<a href="{0}" target="_blank">{0}</a>', instance.report_url)


admin.site.register(Notification, NotificationAdmin)
admin.site.register(Report, ReportAdmin)
