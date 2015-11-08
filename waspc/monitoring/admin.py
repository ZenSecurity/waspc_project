from .models import Monitor
from django.contrib import admin


@admin.register(Monitor)
class MonitorAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'periodic_task', 'modified')
