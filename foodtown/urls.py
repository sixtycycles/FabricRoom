from django.urls import path
from foodtown.views import SnackCreateView, SnackListView, SnackOrderView

urlpatterns = [
    path("", SnackListView.as_view(), name="snack_list"),
    path("new/", SnackCreateView.as_view(), name="snack_new"),
    path("order/", SnackOrderView.as_view(), name="snack_order"),
]
