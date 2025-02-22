from django.urls import path
from .views import TransactionListView, toggle_flag, approve_transaction, fail_transaction, TransactionReportView

urlpatterns = [
    path("", TransactionListView.as_view(), name="index"),
    path("flag/<int:pk>", toggle_flag, name="flag"),
    path("approve/<int:pk>/", approve_transaction, name="approve_transaction"),
    path("fail/<int:pk>/", fail_transaction, name="fail_transaction"),
    path("report/", TransactionReportView.as_view(), name="report")
]
