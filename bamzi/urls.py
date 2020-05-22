from django.urls import path

from bamzi.views import import_share_data

urlpatterns = [
    path('', import_share_data),
]