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
    access = (user.username == username)
    if not access:
        return render(request, 'bamzi/user_share.html', {})
    if request.method == 'POST':
        share_id = request.POST.get('share_id', '')
        count = request.POST.get('count', 0)
        basic_price = request.POST.get('basic_price', 0)
        if share_id and count and basic_price:
            share = Share.objects.filter(pk=share_id).first()
            count = int(count)
            basic_price = int(basic_price)
            if share:
                user_share = UserShare.objects.create(user=user,
                share=share, count=count, basic_price=basic_price,
                relative_max_price=basic_price,
                relative_min_price=basic_price)
    
    user_shares = UserShare.objects.filter(user=user)
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
                                    'industry': u_share.share.industry.name})
    return render(request, 'bamzi/user_share.html', {'user_shares':user_shares_result})


def edit_user_share(request, share_id):
    if request.method == 'POST':
        user_share = UserShare.objects.filter(pk=share_id, user=request.user).first()
        if user_share:
            count = request.POST.get('count', 0)
            basic_price = request.POST.get('basic_price', 0)
            user_share.count = count
            user_share.basic_price = basic_price
            user_share.save()
    return HttpResponseRedirect(reverse('my_shares', kwargs={'username': request.user.username}))


def my_precedence_shares(request, username):
    user = request.user
    access = (user.username == username)
    if not access:
        return render(request, 'bamzi/user_precedence_share.html', {})
    if request.method == 'POST':
        precedence_share_id = request.POST.get('share_id', '')
        count = int(request.POST.get('count', 0))
        precedence_share = PrecedenceShare.objects.filter(pk=precedence_share_id).first()
        if precedence_share:
            user_precedence_share = UserPrecedenceShare.objects.create(user=user,
            precedence_share=precedence_share, count=count, done=False)
    
    user_precedence_shares = UserPrecedenceShare.objects.filter(user=user)
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
                                    'is_open': up_share.precedence_share.share.is_open})

    return render(request, 'bamzi/user_precedence_share.html', {'user_precedence_shares':result})


def my_convention_benefit(request, username):
    user = request.user
    access = (user.username == username)
    if not access:
        return render(request, 'bamzi/user_convention_benefit.html', {})
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
                                    'is_open': benefit.convention_benefit.share.is_open})

    return render(request, 'bamzi/user_convention_benefit.html', {'user_convention_benefits':result})


def my_industry(request, username):
    user = request.user
    access = (user.username == username)
    if not access:
        return render(request, 'bamzi/user_industry_chart.html', {})
    result = UserShare.objects.filter(user=user).values('share__industry__name').annotate(
        total_price=Sum(F('count')*F('share__final_price'),
        output_field=models.FloatField())
    )
    total_share_price = sum(item['total_price'] for item in result)
    industry_percent = {}
    for item in result:
        industry_percent[item['share__industry__name']] = round(item['total_price'] / total_share_price * 100, 2)
    empty_industry = Industry.objects.exclude(name__in=industry_percent).annotate(num_shares=Count('shares')).order_by('-num_shares').values('name', 'num_shares')
    return render(request, 'bamzi/user_industry_chart.html', {'empty_industry': empty_industry, 'industry_percent': industry_percent})


def share_convention(request):
    share_conventions = ShareConvention.objects.all()
    share_convention_result = []
    for share_c in share_conventions:
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
                                    'industry': share_c.share.industry.name})
    return render(request, 'bamzi/share_convention.html', {'share_conventions':share_convention_result})


def update_share_data(request):
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
            
            share.last_price = int(share_data[7])
            share.final_price = int(share_data[6])
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

    return render(request, 'bamzi/chart.html', {'share_data': share_data})