from .models import Report
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.html import format_html


@admin.register(Report)
class ScannerAdmin(admin.ModelAdmin):
    def id(instance):
        instance_pk = instance.pk
        return format_html(
            '<a href="{0}" target="_blank">{1}</a>',
            reverse(viewname='scanner:report', args=[instance_pk]),
            instance_pk
        )

    def target_url(instance):
        return format_html('<a href="{0}" target="_blank">{0}</a>', instance.target_url)

    list_display = (id, target_url, 'modified')
    search_fields = ('id',)
