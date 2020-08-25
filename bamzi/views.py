from django.shortcuts import render
import pandas as pd
import requests
from BamziTrader.settings import BASE_DIR


def import_share_data(request):
    tse_response = requests.get('http://www.tsetmc.com/tsev2/data/MarketWatchInit.aspx?h=0&r=0')
    if tse_response.status_code == 200:
        tse_data = tse_response.text.split(';')
        tse_data = map(lambda x: x.split(','), tse_data)
    share_data = pd.read_csv('{}/bamzi/helpers/all_shares.csv'.format(BASE_DIR))
    return render(request, 'bamzi/index.html', {'share_data': share_data})