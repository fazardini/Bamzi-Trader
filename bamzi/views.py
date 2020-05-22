from django.shortcuts import render
import numpy as np

from BamziTrader.settings import BASE_DIR


def import_share_data(request):
    share_data = np.loadtxt('{}/bamzi/helpers/all_shares.csv'.format(BASE_DIR),
                               delimiter=',', skiprows=1, dtype=str)
    return render(request, 'bamzi/index.html', {'share_data': share_data[0]})