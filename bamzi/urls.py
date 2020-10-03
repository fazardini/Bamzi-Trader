from django.urls import path

from bamzi.views import update_share_data, user_login, user_logout, my_shares, shares_name, share_convention

urlpatterns = [
    path('share/update/', update_share_data),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('shares/<username>/', my_shares, name='my_shares'),
    path('shares-name/', shares_name, name='shares_name'),
    path('shares-convention/', share_convention, name='share_convention'),
]