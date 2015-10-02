from .models import Monitor
from django.contrib import admin


class MonitorAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'periodic_task', 'modified')


admin.site.register(Monitor, MonitorAdmin)
