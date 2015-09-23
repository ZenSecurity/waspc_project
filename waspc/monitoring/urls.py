from .views import MonitorViewSet
from rest_framework.routers import DefaultRouter


monitor_router = DefaultRouter()
monitor_router.register(r'monitor', MonitorViewSet, base_name='monitor')
