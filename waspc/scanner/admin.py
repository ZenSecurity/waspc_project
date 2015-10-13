from .models import ScanReport
from django.contrib import admin
from django.utils.html import format_html


class ScannerAdmin(admin.ModelAdmin):
    fields = ('id', 'target_url_link', 'result_url_link', 'modified')
    readonly_fields = ('id', 'target_url_link', 'result_url', 'result_url_link', 'modified')
    search_fields = ('id',)

    def result_url_link(self, instance):
        return format_html('<a href="{0}" target="_blank">{0}</a>', instance.result_url)

    def target_url_link(self, instance):
        return format_html('<a href="{0}" target="_blank">{0}</a>', instance.target_url)


admin.site.register(ScanReport, ScannerAdmin)
