from .views import ReportTemplateView, ScannerTemplateView
from django.conf.urls import url


urlpatterns = [
    url(r'^$', ScannerTemplateView.as_view(), name='root'),
    url(r'^report/(?P<pk>[0-9a-f-]+)/$', ReportTemplateView.as_view(), name='report')
]
