from .views import ReportTemplateView, ProcessReportTemplateView
from django.conf.urls import url


urlpatterns = [
    url(r'^process/(?P<pk>[0-9a-f-]+)/$', ProcessReportTemplateView.as_view(), name='process'),
    url(r'^report/(?P<pk>[0-9a-f-]+)/$', ReportTemplateView.as_view(), name='report')
]
