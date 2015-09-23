from .models import ScanReport
from django.contrib import admin


class ScannerAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'result_url', 'target_url')


admin.site.register(ScanReport, ScannerAdmin)
