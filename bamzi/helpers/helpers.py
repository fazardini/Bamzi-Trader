import numpy as np
from BamziTrader.settings import BASE_DIR


def shares_csv_to_array():
    share_data = np.loadtxt('{}/bamzi/helpers/all_shares.csv'.format(BASE_DIR),
                               delimiter=',', skiprows=1, dtype=str)
    return share_data


def persian_text_normalizer(text):
    text.replace('ك', 'ک')
    text.replace('ي', 'ی')
    return text