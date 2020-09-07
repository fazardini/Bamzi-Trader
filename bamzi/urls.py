from django.urls import path

from bamzi.views import update_share_data, user_login, user_logout, my_share

urlpatterns = [
    path('share/update/', update_share_data),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('shares/<username>/', my_share, name='my_share')
]