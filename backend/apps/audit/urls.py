from django.urls import path
from .views import AuditLogListView, BiometricAuditLogView, AuditBatchSyncView

urlpatterns = [
    path('audit-logs', AuditLogListView.as_view(), name='audit-logs-list'),
    path('audit-logs/biometric', BiometricAuditLogView.as_view(), name='audit-logs-biometric'),
    path('audit-logs/batch', AuditBatchSyncView.as_view(), name='audit-logs-batch'),
]
