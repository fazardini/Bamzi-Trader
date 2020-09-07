from django.shortcuts import render
import pandas as pd
import requests
from BamziTrader.settings import BASE_DIR
from bamzi.models import Share
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
                    return HttpResponseRedirect(reverse('my_share', kwargs={'username': user.username}))
                else:
                    return render(request, 'bamzi/login.html', {'error': True})
            else:
                return render(request, 'bamzi/login.html', {'active_error': True})
        else:
            return render(request, 'bamzi/login.html', {'error': True})
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('my_share', kwargs={'username': request.user.username}))
    else:
        return render(request, 'bamzi/login.html', {})


def user_logout(request):

    logout(request)
    return HttpResponseRedirect(reverse('login'))


def my_share(request, username):
    return render(request, 'bamzi/index.html', {'share_data': {}})


def update_share_data(request):
    tn = TextNormalizer(TextNormalizerConfig.NORMAL_NAME_CONFIG)
    tse_response = requests.get('http://www.tsetmc.com/tsev2/data/MarketWatchInit.aspx?h=0&r=0')
    if tse_response.status_code == 200:
        tse_data = tse_response.text.split(';')
        tse_data = list(map(lambda x: x.split(','), tse_data))
        tse_data = list(filter(lambda x: not hasNumbers(x[2]) and len(x)==23, tse_data))
        for share_data in tse_data:
            share = Share.objects.filter(tse_id=share_data[0]).first()
            if not share:
                share = Share.objects.create(tse_id=share_data[0])
                share.symbol_name = tn.normalize_text(share_data[2])
                share.company_name = tn.normalize_text(share_data[3])
            
            share.last_price = share_data[7]
            share.final_price = share_data[6]
            share.eps = 0 if not share_data[14] else int(share_data[14])
            share.save()

    return render(request, 'bamzi/index.html', {'share_data': share_data})