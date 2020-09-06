from django.urls import path

from bamzi.views import update_share_data

urlpatterns = [
    path('share/update/', update_share_data),
]