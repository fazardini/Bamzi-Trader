from django.urls import path

from bamzi.views import *

urlpatterns = [
    path('share/update/', update_share_data),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('shares/<username>/', my_shares, name='my_shares'),
    path('precedence_shares/<username>/', my_precedence_shares, name='my_precedence_shares'),

    path('shares-name/', shares_name, name='shares_name'),
    path('precedence-shares-name/', precedence_shares_name, name='precedence_shares_name'),
    path('shares-convention/', share_convention, name='share_convention'),
]