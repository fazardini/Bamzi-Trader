from django.shortcuts import render
import requests
import json
from BamziTrader.settings import BASE_DIR
from bamzi.models import *
from bamzi.helpers.text_helpers import *
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.urls import reverse
from django.db.models import Sum, F, Count


def admin_user_shares(request):
    user = request.user
    if not user.is_superuser:
        return HttpResponseRedirect(reverse('login'))
    
    user_shares = UserShare.objects.all()
    user_shares_result = []
    for u_share in user_shares:
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
                                    'user': u_share.user.username})
    return render(request, 'bamzi/user_shares_admin.html', {'user_shares':user_shares_result})


def admin_user_precedence_shares(request):
    user = request.user
    if not user.is_superuser:
        return HttpResponseRedirect(reverse('login'))

    user_precedence_shares = UserPrecedenceShare.objects.all()
    result = []
    for up_share in user_precedence_shares:
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
                                    'user': up_share.user.username})

    return render(request, 'bamzi/precedence_share_admin.html', {'user_precedence_shares':result})



def admin_user_convention_benefit(request):
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
