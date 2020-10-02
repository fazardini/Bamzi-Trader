from django.shortcuts import render
import requests
import json
from BamziTrader.settings import BASE_DIR
from bamzi.models import Share, UserShare
from bamzi.helpers.text_helpers import *
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.urls import reverse


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


def my_shares(request, username):
    user = request.user
    access = (user.username == username)
    if not access:
        return render(request, 'bamzi/index.html', {})
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
                                    'is_open': u_share.share.is_open})
    return render(request, 'bamzi/index.html', {'user_shares':user_shares_result})


# def my_share(request, username):
#     return render(request, 'bamzi/index.html', {'share_data': {}})


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

    return render(request, 'bamzi/index.html', {'share_data': share_data})