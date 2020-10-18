from django.shortcuts import render
import requests
import json
from BamziTrader.settings import BASE_DIR
from bamzi.models import *
from bamzi.helpers.helpers import cal_remaining_up
from bamzi.helpers.text_helpers import *
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.urls import reverse


def admin_user_shares(request):
    user = request.user
    if not user.is_superuser:
        return HttpResponseRedirect(reverse('login'))
    
    user_shares = UserShare.objects.all()
    user_shares_result = []
    for u_share in user_shares:
        if u_share.share.yesterday_price:
            last_price_percent = round((u_share.share.last_price - u_share.share.yesterday_price)/u_share.share.yesterday_price * 100, 2)
            final_price_percent = round((u_share.share.final_price - u_share.share.yesterday_price)/u_share.share.yesterday_price * 100, 2)
        else:
            last_price_percent = 0
            final_price_percent = 0
        user_shares_result.append({ 'id': u_share.id, 
                                    'symbol_name': u_share.share.symbol_name,
                                    'company_name': u_share.share.company_name,
                                    'basic_price': u_share.basic_price,
                                    'last_price': u_share.share.last_price,
                                    'final_price': u_share.share.final_price,
                                    'count': u_share.count,
                                    'profit_loss':u_share.profit_loss,
                                    'target': u_share.target,
                                    'is_open': u_share.share.is_open,
                                    'market_type': u_share.share.get_market_type_display(),
                                    'industry': u_share.share.industry.name,
                                    'got_averaged': u_share.got_averaged,
                                    'user': u_share.user.username,
                                    'last_price_percent': last_price_percent,
                                    'final_price_percent': final_price_percent,
                                    'tp1': u_share.share.tp1})
    return render(request, 'bamzi/user_shares_admin.html', {'user_shares':user_shares_result})


def admin_precedence_shares(request):
    user = request.user
    if not user.is_superuser:
        return HttpResponseRedirect(reverse('login'))

    user_precedence_shares = UserPrecedenceShare.objects.all()
    result = []
    for up_share in user_precedence_shares:
        remaining_up = None
        if up_share.precedence_share.to_date:
            remaining_up = cal_remaining_up(up_share.precedence_share.to_date)
        result.append({ 'id': up_share.id, 
                                    'symbol_name': up_share.precedence_share.share.symbol_name,
                                    'main_share': up_share.precedence_share.main_share.symbol_name,
                                    'last_price': up_share.precedence_share.share.last_price,
                                    'main_last_price': up_share.precedence_share.main_share.last_price,
                                    'count': up_share.count,
                                    'from_date': up_share.precedence_share.from_date,
                                    'to_date': up_share.precedence_share.to_date,
                                    'convert': up_share.precedence_share.convert,
                                    'stock_affair': up_share.precedence_share.main_share.stock_affair,
                                    'is_open': up_share.precedence_share.share.is_open,
                                    'act': up_share.get_act_display(),
                                    'user': up_share.user.username,
                                    'remaining_up': remaining_up})

    return render(request, 'bamzi/precedence_share_admin.html', {'user_precedence_shares':result})



def admin_convention_benefit(request):
    user = request.user
    if not user.is_superuser:
        return HttpResponseRedirect(reverse('login'))

    user_convention_benefits = UserConventionBenefit.objects.all()
    result = []
    for benefit in user_convention_benefits:
        result.append({ 'id': benefit.id, 
                                    'symbol_name': benefit.convention_benefit.share.symbol_name,
                                    'benefit_price': benefit.benefit_price,
                                    'from_date': benefit.convention_benefit.from_date,
                                    'to_date': benefit.convention_benefit.to_date,
                                    'bank': benefit.convention_benefit.get_bank_display(),
                                    'is_open': benefit.convention_benefit.share.is_open,
                                    'got_it': benefit.got_it,
                                    'user': benefit.user.username})

    return render(request, 'bamzi/convention_benefit_admin.html', {'user_convention_benefits':result})


def update_share_data(request):
    user = request.user
    if not user.is_superuser or request.method != 'POST':
        return HttpResponseRedirect(reverse('login'))
    
    share_data = {}
    tn = TextNormalizer(TextNormalizerConfig.NORMAL_NAME_CONFIG)
    tse_response = requests.get('http://www.tsetmc.com/tsev2/data/MarketWatchInit.aspx?h=0&r=0')
    if tse_response.status_code == 200:
        tse_data = tse_response.text.split(';')
        tse_data = list(map(lambda x: x.split(','), tse_data))
        tse_data = list(filter(lambda x: not hasNumbers(x[2]) and len(x)==23, tse_data))
        Share.objects.all().update(is_open=False)
        for share_data in tse_data:
            share = Share.objects.filter(tse_id=share_data[0]).first()
            if not share:
                share = Share.objects.create(tse_id=share_data[0])
                share.symbol_name = tn.normalize_text(share_data[2])
                share.company_name = tn.normalize_text(share_data[3])
                industry = Industry.objects.filter(code=int(share_data[18])).first()
                share.industry = industry
            
            if not share.industry:
                industry = Industry.objects.filter(code=int(share_data[18])).first()
                share.industry = industry
            share.last_price = int(share_data[7])
            share.final_price = int(share_data[6])
            share.yesterday_price = int(share_data[13])
            share.eps = 0 if not share_data[14] else int(share_data[14])
            # if share.absolute_max_price:
            #     share.absolute_max_price = max(share.absolute_max_price, share.final_price)
            # if share.absolute_min_price:
            #     share.absolute_min_price = min(share.absolute_min_price, share.final_price)
            share.is_open = True
            share.save()
            user_shares = UserShare.objects.filter(share=share)
            
            for user_share in user_shares:
                user_share.relative_max_price = max(share.final_price, user_share.relative_max_price)
                user_share.relative_min_price = min(share.final_price, user_share.relative_min_price)
                user_share.save()

    return HttpResponseRedirect(reverse('admin_user_shares'))