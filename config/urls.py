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
from rest_framework.routers import DefaultRouter
from waspc.monitoring.views import MonitorViewSet
from waspc.reporting.views import NotificationViewSet
from waspc.reporting.views import ReportViewSet
from waspc.reporting.urls import urlpatterns as reporting_urlpatterns
from waspc.scanner.views import ScannerViewSet
from waspc.scanner.urls import urlpatterns as scanner_urlpatterns


api_router = DefaultRouter()
api_router.register(r'monitoring', MonitorViewSet, 'monitoring')
api_router.register(r'notification', NotificationViewSet, 'notification')
api_router.register(r'reporting', ReportViewSet, 'reporting')
api_router.register(r'scanner', ScannerViewSet, 'scanner')

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(api_router.urls, namespace='api')),
    url(r'^scanner/', include(scanner_urlpatterns, namespace='scanner')),
    url(r'^reporting/', include(reporting_urlpatterns, namespace='reporting'))
]
