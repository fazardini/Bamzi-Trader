from django.urls import path

from bamzi.views import *

urlpatterns = [
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('shares/<username>/', my_shares, name='my_shares'),
    path('precedence-shares/<username>/', my_precedence_shares, name='my_precedence_shares'),
    path('convention-benefit/<username>/', my_convention_benefit, name='my_convention_benefit'),
    path('industry-chart/<username>/', my_industry, name='my_industry'),
    path('user-shares/<share_id>/', edit_user_share, name='edit_user_shares'),
    path('user-precedence-shares/<share_id>/', edit_user_precedence_shares, name='edit_user_precedence_shares'),
    path('user-convention-benefit/<share_id>/', edit_user_convention_benefit, name='edit_user_convention_benefit'),

    path('shares-name/', shares_name, name='shares_name'),
    path('precedence-shares-name/', precedence_shares_name, name='precedence_shares_name'),
    path('convention-benefit-name/', convention_benefit_name, name='convention_benefit_name'),
    path('shares-convention/', share_convention, name='share_convention'),

    path('import-csv-shares/<username>/', import_csv_shares, name='import_csv_shares'),
]