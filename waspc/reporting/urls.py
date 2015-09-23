from .views import (NotificationViewSet,
                    ReportRetrieveAPIView,
                    ReportViewSet)
from django.conf.urls import url
from rest_framework.routers import DefaultRouter


report_router = DefaultRouter()
report_router.register(r'report', ReportViewSet, base_name='report')

report_view_url = [
    url(r'^report/(?P<pk>[0-9a-f-]+)/$', ReportRetrieveAPIView.as_view(), name='report-view')
]

notification_router = DefaultRouter()
notification_router.register(r'notification', NotificationViewSet, base_name='notification')
