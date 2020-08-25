import pandas as pd
from BamziTrader.settings import BASE_DIR


def csv_to_array(file_name):
    read_data = pd.read_csv('{}/bamzi/helpers/{}.csv'.format(BASE_DIR, file_name))
    return read_data


def persian_text_normalizer(text):
    text.replace('ك', 'ک')
    text.replace('ي', 'ی')
    text.replace('\u200C', ' ')
    text.replace('\u202F', ' ')
    text.replace(' ', ' ')
    return text
