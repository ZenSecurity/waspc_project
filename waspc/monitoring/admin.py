from .models import Monitor
from django.contrib import admin


class MonitorAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'periodic_task')


admin.site.register(Monitor, MonitorAdmin)
