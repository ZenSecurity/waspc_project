from .views import HistoryReportTemplateView, ProcessReportTemplateView
from django.conf.urls import url


urlpatterns = [
    url(r'^process/(?P<pk>[0-9a-f-]+)/$', ProcessReportTemplateView.as_view(), name='process'),
    url(r'^history/(?P<pk>[0-9a-f-]+)/$', HistoryReportTemplateView.as_view(), name='history')
]
