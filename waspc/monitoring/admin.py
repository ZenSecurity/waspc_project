from .models import Monitor
from django.contrib import admin


@admin.register(Monitor)
class MonitorAdmin(admin.ModelAdmin):
    def name(self, instance):
        return instance.periodic_task.name

    def interval(self, instance):
        return instance.periodic_task.interval

    list_display = ('name', 'interval', 'modified')
