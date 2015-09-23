"""waspc URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from waspc.monitoring.urls import monitor_router
from waspc.reporting.urls import (notification_router,
                                  report_router,
                                  report_view_url)
from waspc.scanner.views import ScannerTemplateView
from waspc.scanner.urls import scanner_report_url, scanner_router


urlpatterns = [
    url(r'^$', ScannerTemplateView.as_view()),
    url(r'^admin/', include(admin.site.urls)),
    # url(r'^api/', include(monitor_router.urls + scanner_router.urls)),
    url(r'^api/', include(monitor_router.urls + report_router.urls + notification_router.urls)),
    # url(r'', include(scanner_report_url)),
    url(r'', include(report_view_url))
]
