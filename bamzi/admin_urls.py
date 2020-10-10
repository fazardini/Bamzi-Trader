from django.urls import path

from bamzi.admin_views import *

urlpatterns = [
    path('user-shares/', admin_user_shares, name='admin_user_shares'),
    path('user-precedence-shares/', admin_user_precedence_shares, name='admin_precedence_shares'),
    path('user-convention-benefit/', admin_user_convention_benefit, name='admin_convention_benefit'),

]