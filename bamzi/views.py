from django.shortcuts import render
import requests
import json
import csv
from io import StringIO
from BamziTrader.settings import BASE_DIR
from bamzi.models import *
from bamzi.helpers.text_helpers import *
from bamzi.helpers.helpers import get_user_alert, cal_remaining_up
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.urls import reverse
from django.db.models import Sum, F, Count


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = User.objects.filter(username=username).first()
        if user:
            if user.is_active:
                user = authenticate(username=username, password=password)
                if user:
                    login(request, user)
                    return HttpResponseRedirect(reverse('my_shares', kwargs={'username': user.username}))
                else:
                    return render(request, 'bamzi/login.html', {'error': True})
            else:
                return render(request, 'bamzi/login.html', {'active_error': True})
        else:
            return render(request, 'bamzi/login.html', {'error': True})
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('my_shares', kwargs={'username': request.user.username}))
    else:
        return render(request, 'bamzi/login.html', {})


def user_logout(request):

    logout(request)
    return HttpResponseRedirect(reverse('login'))


def shares_name(request):
    if request.is_ajax():
        searched_text = request.GET.get('term', '')
        shares = Share.objects.filter(symbol_name__icontains=searched_text).distinct().values(
            'symbol_name', 'id').order_by('symbol_name')[:10]
        results = []
        for share in shares:
            share_json = {'label': share['symbol_name'], 'value': share['symbol_name'],
                          'id': share['id']}
            results.append(share_json)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


def precedence_shares_name(request):
    if request.is_ajax():
        searched_text = request.GET.get('term', '')
        shares = PrecedenceShare.objects.filter(share__symbol_name__icontains=searched_text).distinct().values(
            'id', 'share__symbol_name').order_by('share__symbol_name')[:10]
        results = []
        for share in shares:
            share_json = {'label': share['share__symbol_name'], 'value': share['share__symbol_name'],
                          'id': share['id']}
            results.append(share_json)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


def convention_benefit_name(request):
    if request.is_ajax():
        searched_text = request.GET.get('term', '')
        shares = ConventionBenefit.objects.filter(share__symbol_name__icontains=searched_text).distinct().values(
            'id', 'share__symbol_name').order_by('share__symbol_name')[:10]
        results = []
        for share in shares:
            share_json = {'label': share['share__symbol_name'], 'value': share['share__symbol_name'],
                          'id': share['id']}
            results.append(share_json)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


def my_shares(request, username):
    user = request.user
    access = (user.username == username) or user.is_superuser
    if not access:
        return HttpResponseRedirect(reverse('login'))
    if request.method == 'POST':
        share_id = request.POST.get('share_id', '')
        count = request.POST.get('count', 0)
        basic_price = request.POST.get('basic_price', 0)
        if share_id and count and basic_price:
            share = Share.objects.filter(pk=share_id).first()
            count = int(count)
            basic_price = int(basic_price)
            user_share = UserShare.objects.filter(share=share, user=user).exists()
            if share and not user_share:
                user_share = UserShare.objects.create(user=user,
                share=share, count=count, basic_price=basic_price,
                relative_max_price=basic_price,
                relative_min_price=basic_price)
    
    user_shares = UserShare.objects.filter(user=user, count__gt=0)
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
                                    'last_price_percent': last_price_percent,
                                    'final_price_percent': final_price_percent,
                                    'tp1': u_share.share.tp1})
    alerts = get_user_alert(user)
    return render(request, 'bamzi/user_share.html', {'user_shares':user_shares_result, 'alerts': alerts})


def edit_user_share(request, share_id):
    if request.method == 'POST':
        user_share = UserShare.objects.filter(pk=share_id, user=request.user).first()
        if user_share:
            count = request.POST.get('count', 0)
            basic_price = request.POST.get('basic_price', 0)
            got_averaged = request.POST.get('got_averaged', False)
            got_averaged = bool(got_averaged)
            user_share.count = count
            user_share.basic_price = basic_price
            user_share.got_averaged = got_averaged
            user_share.save()
    return HttpResponseRedirect(reverse('my_shares', kwargs={'username': request.user.username}))


def edit_user_precedence_shares(request, share_id):
    if request.method == 'POST':
        user_precedence_share = UserPrecedenceShare.objects.filter(pk=share_id, user=request.user).first()
        if user_precedence_share:
            count = request.POST.get('count', 0)
            act = request.POST.get('act', 0)
            user_precedence_share.count = count
            user_precedence_share.act = act
            user_precedence_share.save()
    return HttpResponseRedirect(reverse('my_precedence_shares', kwargs={'username': request.user.username}))


def edit_user_convention_benefit(request, share_id):
    if request.method == 'POST':
        user_convention_benefit = UserConventionBenefit.objects.filter(pk=share_id, user=request.user).first()
        if user_convention_benefit:
            benefit_price = request.POST.get('benefit_price', 0)
            got_it = request.POST.get('got_it', False)
            got_it = bool(got_it)
            user_convention_benefit.benefit_price = benefit_price
            user_convention_benefit.got_it = got_it
            user_convention_benefit.save()
    return HttpResponseRedirect(reverse('my_convention_benefit', kwargs={'username': request.user.username}))


def my_precedence_shares(request, username):
    user = request.user
    access = (user.username == username) or user.is_superuser
    if not access:
        return HttpResponseRedirect(reverse('login'))
    if request.method == 'POST':
        precedence_share_id = request.POST.get('share_id', '')
        count = int(request.POST.get('count', 0))
        precedence_share = PrecedenceShare.objects.filter(pk=precedence_share_id).first()
        if precedence_share:
            user_precedence_share = UserPrecedenceShare.objects.create(user=user,
            precedence_share=precedence_share, count=count)
    
    user_precedence_shares = UserPrecedenceShare.objects.filter(user=user)
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
                                    'remaining_up': remaining_up})
    alerts = get_user_alert(user)
    return render(request, 'bamzi/user_precedence_share.html', {'user_precedence_shares':result, 'alerts': alerts})


def my_convention_benefit(request, username):
    user = request.user
    access = (user.username == username) or user.is_superuser
    if not access:
        return HttpResponseRedirect(reverse('login'))
    if request.method == 'POST':
        convention_benefit_id = request.POST.get('share_id', '')
        benefit_price = int(request.POST.get('benefit_price', 0))
        convention_benefit = ConventionBenefit.objects.filter(pk=convention_benefit_id).first()
        if convention_benefit:
            user_convention_benefit = UserConventionBenefit.objects.create(user=user,
            convention_benefit=convention_benefit, benefit_price=benefit_price, got_it=False)
    
    user_convention_benefits = UserConventionBenefit.objects.filter(user=user)
    result = []
    for benefit in user_convention_benefits:
        result.append({ 'id': benefit.id, 
                                    'symbol_name': benefit.convention_benefit.share.symbol_name,
                                    'benefit_price': benefit.benefit_price,
                                    'from_date': benefit.convention_benefit.from_date,
                                    'to_date': benefit.convention_benefit.to_date,
                                    'bank': benefit.convention_benefit.get_bank_display(),
                                    'is_open': benefit.convention_benefit.share.is_open,
                                    'got_it': benefit.got_it})
    alerts = get_user_alert(user)
    return render(request, 'bamzi/user_convention_benefit.html', {'user_convention_benefits':result, 'alerts': alerts})


def my_industry(request, username):
    user = request.user
    access = (user.username == username) or user.is_superuser
    if not access:
        return HttpResponseRedirect(reverse('login'))
    result = UserShare.objects.filter(user=user).values('share__industry__name').annotate(
        total_price=Sum(F('count')*F('share__final_price'),
        output_field=models.FloatField())
    )
    total_share_price = sum(item['total_price'] for item in result)
    industry_percent = {}
    for item in result:
        industry_percent[item['share__industry__name']] = round(item['total_price'] / total_share_price * 100, 2)
    empty_industry = Industry.objects.exclude(name__in=industry_percent).annotate(num_shares=Count('shares')).order_by('-num_shares').values('name', 'num_shares')
    alerts = get_user_alert(user)
    return render(request, 'bamzi/user_industry_chart.html', {'empty_industry': empty_industry, 'industry_percent': industry_percent, 'alerts': alerts})


def share_convention(request):
    share_conventions = ShareConvention.objects.all()
    share_convention_result = []
    for share_c in share_conventions:
        user_share_exists = UserShare.objects.filter(user=request.user, count__gt=0, share=share_c.share).exists()
        remaining_up = None
        if share_c.convention_date:
            remaining_up = cal_remaining_up(share_c.convention_date)
        share_convention_result.append({ 'id': share_c.id, 
                                    'symbol_name': share_c.share.symbol_name,
                                    'company_name': share_c.share.company_name,
                                    'convention_date': share_c.convention_date,
                                    'accumulated_profit': share_c.accumulated_profit,
                                    'revaluation': share_c.revaluation,
                                    'cash_priority': share_c.cash_priority,
                                    'level': share_c.level,
                                    'level_str': share_c.get_level_display(),
                                    'is_open': share_c.share.is_open,
                                    'industry': share_c.share.industry.name,
                                    'user_has': user_share_exists,
                                    'remaining_up': remaining_up})
    alerts = get_user_alert(request.user)
    return render(request, 'bamzi/share_convention.html', {'share_conventions':share_convention_result, 'alerts': alerts})


def import_csv_shares(request, username):
    user = request.user
    access = (user.username == username) or user.is_superuser
    file = request.FILES['file_data'].read().decode('utf-8')
    if not access or not file:
        return HttpResponseRedirect(reverse('login'))
    firstline = True
    user_share_list = []
    tn = TextNormalizer(TextNormalizerConfig.NORMAL_NAME_CONFIG)
    csv_data = csv.reader(StringIO(file), delimiter=',')
    csv_data_list = []
    for row in csv_data:
        if firstline:
            firstline = False
            continue
        user_share_list.append(tn.normalize_text(row[0]))
        csv_data_list.append(row)
    all_share_list = Share.objects.all().values_list('symbol_name', flat=True)
    not_exists_shares = list(set(user_share_list) - set(all_share_list))
    if not_exists_shares:
        return render(request, 'bamzi/user_share.html', {'not_exists_shares':not_exists_shares})

    for row in csv_data_list:
        if firstline:
            firstline = False
            continue
        share = Share.objects.filter(symbol_name=tn.normalize_text(row[0])).first()
        UserShare.objects.create(user=user,
                share=share, count=int(row[1]), basic_price=int(row[2]),
                relative_max_price=int(row[2]),
                relative_min_price=int(row[2]))

    return HttpResponseRedirect(reverse('my_shares', kwargs={'username': user.username}))