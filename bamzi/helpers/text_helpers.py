# from __future__ import unicode_literals
import re


def maketrans(aa, bb):
    return dict((ord(a), b) for a, b in zip(aa, bb))

ENGLISH_DIGIT_TRANS = maketrans('1234567890', '۱۲۳۴۵۶۷۸۹۰')
ARABIC_TRANS = maketrans('كي١٢٣٤٥٦٧٨٩٠', 'کی۱۲۳۴۵۶۷۸۹۰')
HAMZAH_TRANS = maketrans('أؤإئء', 'اوای ')
A_MADDAR_TRANS = maketrans('آ', 'ا')
# 'ZERO WIDTH JOINER':  (U+200D), Zero-Width Non-Joiner: U+200C, Narrow No-Break Space: U+202F
SPACE_TRANS = maketrans('\u200C\u202F ', '   ')
# reserved url characters  ; / ? : @ = &   so encode them in url
INVALID_CHARS = ''
DIAGRITICS = '\u064B\u064C\u064D\u064E\u064F\u0650\u0652\u0654\u0655'
#    remove FATHATAN, DAMMATAN, KASRATAN, FATHA, DAMMA, KASRA, SUKUN, HamzaAbove, hamzaB
TASHDID = '\u0651'  # SHADDA,
KESHIDEH = '\u0651'  # KESHIDEH,

# Arabic letter Heh goal : (U+06C1)

# U+06Fn , Persian 0123456789
# U+066n , Arabic 0123456789


class TextNormalizerConfig:
    REPLACE_AR_EN_CHARS = 2**0
    REPLACE_HAMZAH = 2**1
    REPLACE_A_MADDAR = 2**2
    REMOVE_YA_EZAFEH = 2**3
    REMOVE_TASHDID = 2**4
    REMOVE_DIAVRITICS = 2**5
    REMOVE_BAD_SPACES = 2**6
    REMOVE_KESHIDEH = 2**7
    REPLACE_EN_DIGITS = 2 ** 8

    NORMAL_NAME_CONFIG = 0b111111011
    FULL_NAME_CONFIG = 0b011000001
    CITY_NAME_CONFIG = 0b011000001
    SHORT_NAME_CONFIG = 0b001000001


#
# ک و ی عربی و ة 0
# حذف همزه ها (ا و ی ء) 1
# آ به ا 2
# خانه‌ی ما یه خانه ما 3
# حذف تشدید 4
# حذف اعرابها بجز اًن 5
# حذف نیم فاصله و فاصله اضافه 6
# بــــــــر به بر 7
# و ارقام انگلیسی 8
# حذف کاراکترهای غیر مجاز


class TextNormalizer:
    def __init__(self, config):
        self.config = config
        remove_list = INVALID_CHARS
        if self.config & TextNormalizerConfig.REMOVE_TASHDID:
            remove_list += TASHDID
        if self.config & TextNormalizerConfig.REMOVE_DIAVRITICS:
            remove_list += DIAGRITICS
        if self.config & TextNormalizerConfig.REMOVE_KESHIDEH:
            remove_list += KESHIDEH
        self.remove_pattern = None
        if remove_list:
            self.remove_pattern = (re.compile('[{}]'.format(remove_list)), '')
        self.remove_spaces = (re.compile(r' +'), ' ')  # remove extra spaces
        self.remove_ya_ezafeh = (re.compile(r'([^ ]ه)[\u200c| ]ی '), r'\1 ')  # fix ی space

    def normalize_text(self, text):
        if not text:
            return text
        text = text.strip()
        if self.config & TextNormalizerConfig.REPLACE_AR_EN_CHARS:
            text = text.translate(ARABIC_TRANS)
        if self.config & TextNormalizerConfig.REPLACE_HAMZAH:
            text = text.translate(HAMZAH_TRANS)
        if self.config & TextNormalizerConfig.REPLACE_A_MADDAR:
            text = text.translate(A_MADDAR_TRANS)
        if self.config & TextNormalizerConfig.REMOVE_YA_EZAFEH:
            pattern, repl = self.remove_ya_ezafeh
            text = pattern.sub(repl, text)
        if self.config & TextNormalizerConfig.REMOVE_BAD_SPACES:  # it should apply after remove ya ezafeh
            pattern, repl = self.remove_spaces
            text = pattern.sub(repl, text)
            text = text.translate(SPACE_TRANS)
        if self.config & TextNormalizerConfig.REPLACE_EN_DIGITS:
            text = text.translate(ENGLISH_DIGIT_TRANS)

        if self.remove_pattern is not None:
            pattern, repl = self.remove_pattern
            text = pattern.sub(repl, text)

        return text


def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)