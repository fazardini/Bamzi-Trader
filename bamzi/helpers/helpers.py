from BamziTrader.settings import BASE_DIR
from bamzi.models import *
from django.db.models import F
from django.utils import timezone
from datetime import timedelta


def get_user_alert(user):

    user_shares = UserShare.objects.filter(user=user, share__final_price__gte=F('share__tp1')).values_list('share__symbol_name', flat=True)
    today = timezone.now().date()
    sell_precedence_share = []
    user_precedence_shares = UserPrecedenceShare.objects.filter(user=user, act=0,precedence_share__to_date__range=(today, today+timedelta(days=10))).values('precedence_share__share__symbol_name', 'precedence_share__to_date', 'precedence_share__convert')
    for precedence_share in user_precedence_shares:
        sell_precedence_share.append({
            'symbol_name': precedence_share['precedence_share__share__symbol_name'],
            'act': 'تبدیل' if precedence_share['precedence_share__convert'] else 'فروش',
            'remaining_up': (precedence_share['precedence_share__to_date'] - today).days
        })
    alerts = {'sell_user_shares': user_shares, 'sell_precedence_shares': sell_precedence_share}
    return alerts


def cal_remaining_up(to_date):
    today = timezone.now().date()
    return (to_date - today).days