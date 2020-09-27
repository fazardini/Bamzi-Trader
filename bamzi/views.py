from django.shortcuts import render
import requests
import json
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
    context_dict = {}
    if access:

        # surplus_drugs = SurplusDrug.objects.filter(hospital=hospital).exclude(
        #     Q(expiration_date__lt=the_today()) |
        #     Q(current_count=0)
        # ).distinct()
        # if request.method == 'POST':
        #     sort_by = int(request.POST.get('sorted_by', 0))
        #     drug_type = request.POST.get('drug_type', 'all')
        #     if drug_type != 'all':
        #         surplus_drugs = surplus_drugs.filter(drug_type=drug_type)
        #     if sort_by == 4:
        #         surplus_drugs = surplus_drugs.order_by('current_count')
        #     elif sort_by == 3:
        #         surplus_drugs = surplus_drugs.order_by('-current_count')
        #     elif sort_by == 2:
        #         surplus_drugs = surplus_drugs.order_by('-expiration_date')
        #     elif sort_by == 1:
        #         surplus_drugs = surplus_drugs.order_by('expiration_date')
        #     else:
        #         surplus_drugs = surplus_drugs.order_by('drug__name')
        #     surplus_drugs = surplus_drugs.values(
        #         'safe_id', 'drug__name', 'expiration_date', 'current_count', 'cat',
        #         'drug_type', 'price')
        # surplus_drugs = surplus_drugs.values(
        #     'safe_id', 'drug__name', 'expiration_date', 'current_count', 'cat',
        #     'drug_type', 'price')
        # for drug in surplus_drugs:
        #     drug['ordered'] = not OrderedDrug.objects.filter(surplus_drug__safe_id=drug['safe_id']).exists()
        #     drug['cat'] = SurplusDrug.CAT_DICT[drug['cat']]
        #     drug['drug_type'] = SurplusDrug.TYPE_DICT[drug['drug_type']]
        #     if drug['expiration_date'] - the_today() <= timedelta(days=90):
        #         drug['exp_state'] = "lte3"
        #     elif drug['expiration_date'] - the_today() <= timedelta(days=180):
        #         drug['exp_state'] = "lte6"
        #     else:
        #         drug['exp_state'] = "gt6"
        # context_dict = {'access': access, 'surplus_drugs': list(surplus_drugs),
        #                 'safe_id': request.user.hospital.safe_id,
        #                 'pending_drugs_count': pending_drugs_count(request.user.hospital)}
        if request.method == 'POST':
            return JsonResponse(context_dict)
        return render(request, 'bamzi/shares.html', context_dict)
    else:
        return render(request, 'bamzi/shares.html', {'access': access})

# def my_share(request, username):
#     return render(request, 'bamzi/index.html', {'share_data': {}})


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