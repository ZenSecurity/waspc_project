from .views import (ScannerViewSet,
                    ReportRetrieveAPIView,
                    ReportViewSet)
from django.conf.urls import url
from rest_framework.routers import DefaultRouter


scanner_router = DefaultRouter()
scanner_router.register(r'scanner', ScannerViewSet, base_name='scanner')
scanner_router.register(r'report', ReportViewSet, base_name='report')

scanner_report_url = [
    url(r'^report/(?P<pk>[0-9a-f-]+)/$', ReportRetrieveAPIView.as_view(), name='report-view')
]
