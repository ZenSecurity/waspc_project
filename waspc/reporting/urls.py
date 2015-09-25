from .views import ReportTemplateView
from django.conf.urls import url


urlpatterns = [
    url(r'^report/(?P<pk>[0-9a-f-]+)/$', ReportTemplateView.as_view(), name='report')
]
