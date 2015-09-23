from .models import Notification, Report
from django.contrib import admin


class NotificationAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'report')


class ReportAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'report_url', 'broker')


admin.site.register(Notification, NotificationAdmin)
admin.site.register(Report, ReportAdmin)
