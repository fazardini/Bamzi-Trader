from django.urls import path

from bamzi.admin_views import *

urlpatterns = [
    path('share/update/', update_share_data, name="update_share_data"),
    path('user-shares/', admin_user_shares, name='admin_user_shares'),
    path('user-precedence-shares/', admin_precedence_shares, name='admin_precedence_shares'),
    path('user-convention-benefit/', admin_convention_benefit, name='admin_convention_benefit'),
]